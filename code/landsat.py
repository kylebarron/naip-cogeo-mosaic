"""
Adapted from:
https://github.com/developmentseed/awspds-mosaic/blob/master/notebooks/LargeScaleMosaic.ipynb
"""

import time
import urllib.parse
from concurrent import futures
from datetime import datetime
from io import BytesIO

import click
import mercantile
import rasterio
import requests
from affine import Affine
from dateutil.parser import parse as dateparse
from rasterio.io import MemoryFile
from rasterio.windows import Window
from rio_cogeo.cogeo import cog_translate
from rio_cogeo.profiles import cog_profiles
from rio_cogeo.utils import _meters_per_pixel
from rio_tiler_mosaic.mosaic import _filter_futures
from supermercado.burntiles import tile_extrema

from tqdm.notebook import tqdm

PIXEL_SELECTION_METHODS = [
    'first', 'highest', 'lowest', 'mean', 'median', 'stdev', 'all', 'count',
    'lastband']


@click.command()
@click.option(
    '-b',
    '--bbox',
    type=str,
    required=True,
    help=
    'Comma-separated bounding box of interest, i.e. `-126.71,24.49,-66.59,49.48`'
)
@click.option(
    '--endpoint', type=str, required=True, help='Base URL of endpoint')
@click.option(
    '-o',
    '--out-path',
    type=click.Path(
        file_okay=True, dir_okay=False, writable=True, resolve_path=True),
    required=True,
    help='Output path for tif')
@click.option(
    '--max-cloud',
    type=float,
    required=False,
    default=20,
    show_default=True,
    help='Max cloud percentage')
@click.option(
    '--retina/--no-retina',
    is_flag=True,
    default=True,
    show_default=True,
    help='If True, generates high DPI tiles')
@click.option(
    '--start-date',
    type=str,
    required=False,
    default=None,
    help='Start date to use for mosaic')
@click.option(
    '--end-date',
    type=str,
    required=False,
    default=None,
    help='End date to use for mosaic, inclusive')
@click.option(
    '--pixel-selection',
    type=click.Choice(PIXEL_SELECTION_METHODS, case_sensitive=False),
    required=False,
    default='first',
    help='Pixel selction method.')
def main(
    bbox, endpoint, out_path, max_cloud, retina, start_date, end_date,
    pixel_selection):
    # bbox = '-126.71,24.49,-66.59,49.48'
    bounds = list(map(float, bbox.split(',')))

    if start_date is not None:
        start_date = dateparse(start_date)
    if end_date is not None:
        end_date = dateparse(end_date)

    results = construct_mosaic(
        endpoint=endpoint,
        bounds=bounds,
        max_cloud=max_cloud,
        retina=retina,
        start_date=start_date,
        end_date=end_date)
    tilescale = 2 if retina is True else 1
    tilesize = 256 * tilescale
    zoom = results["maxzoom"] - (tilescale - 1)

    # Mercator tiles covering bounds
    extrema = tile_extrema(bounds, zoom)
    tiles = mercantile.tiles(*bounds, zooms=zoom)

    query_params = {
        # True Color RGB
        'bands': "4,3,2",
        # Looks nice
        'color_ops': "gamma RGB 3.5, saturation 1.7, sigmoidal RGB 15 0.35",
        'pixel_selection': pixel_selection, }
    tiles_url = results["tiles"][0] + urllib.parse.urlencode(query_params)

    assemble_tif(
        out_path=out_path,
        zoom=zoom,
        tiles=tiles,
        tiles_url=tiles_url,
        extrema=extrema,
        tilesize=tilesize)


def construct_mosaic(
    endpoint,
    bounds,
    retina=True,
    max_cloud=20,
    start_date=None,
    end_date=None):
    """Construct Landsat MosaicJSON from bounds
    """
    if start_date is None:
        start_date = datetime.strptime("2019-01-01", "%Y-%m-%d")
    if end_date is None:
        end_date = datetime.strptime("2019-12-31", "%Y-%m-%d")

    try:
        start = start_date.strftime("%Y-%m-%dT00:00:00Z")
    except AttributeError:
        raise ValueError('start_date should be of type datetime.datetime')

    try:
        end = end_date.strftime("%Y-%m-%dT23:59:59Z")
    except AttributeError:
        raise ValueError('end_date should be of type datetime.datetime')

    query = {
        "bbox": bounds,
        "time": f"{start}/{end}",
        "query": {
            "eo:sun_elevation": {
                "gt": 0},
            "landsat:tier": {
                "eq": "T1"},
            "collection": {
                "eq": "landsat-8-l1"},
            "eo:cloud_cover": {
                "gte": 0,
                "lt": max_cloud}},
        "sort": [{
            "field": "eo:cloud_cover",
            "direction": "asc"}]}

    tilescale = 2 if retina is True else 1

    # Landsat covers zoom 7 to 12 but because we don't want to use the mosaic
    # for visualization purpose we don't really care about lower zoom level.
    # We could use zoom 11 but don't want to make the mosaicJSON file too big.
    params = {
        # Minzoom define the quadkey zoom and thus the number of quadkey list
        # See https://github.com/developmentseed/mosaicjson-spec/tree/master/0.0.2
        "minzoom": 9,
        # We filter the season to have greenest data
        "seasons": "spring,summer",
        # Here we can also pass some tile option to be added to the tile url.
        "tile_format": "tif",  # We use GeoTIFF output from the tiler
        "tile_scale": tilescale}

    # We post the query to the mosaic endpoint with some optional parameters
    r = requests.post(f"{endpoint}/mosaic/create", json=query, params=params)
    results = r.json()

    return results


def _call_tile_endpoint(tile, tile_url, extrema, tilesize=256, retry=0):
    """Tile Worker.

    Call the tile endpoint for each mercator tile.
    """
    url = tile_url.format(z=tile.z, x=tile.x, y=tile.y)
    img = requests.get(url)
    if not img.status_code == 200:
        time.sleep(3)
        if retry == 3:
            raise Exception("Empty")
        return _call_tile_endpoint(tile, retry=retry + 1)

    row = (tile.y - extrema["y"]["min"]) * tilesize
    col = (tile.x - extrema["x"]["min"]) * tilesize
    window = Window(col_off=col, row_off=row, width=tilesize, height=tilesize)

    return window, img


def assemble_tif(out_path, zoom, tiles, tiles_url, extrema, tilesize):

    # Define Output COG parameters
    width = (extrema["x"]["max"] - extrema["x"]["min"]) * tilesize
    height = (extrema["y"]["max"] - extrema["y"]["min"]) * tilesize
    w, n = mercantile.xy(
        *mercantile.ul(extrema["x"]["min"], extrema["y"]["min"], zoom))
    res = _meters_per_pixel(zoom, 0, tilesize=tilesize)

    params = {
        'driver': "GTiff",
        'dtype': "uint8",
        'count': 3,
        'width': width,
        'height': height,
        'crs': "epsg:3857",
        'transform': Affine(res, 0, w, 0, -res, n),
        'nodata': 0,
        'tiled': True,
        'blockxsize': tilesize,
        'blockysize': tilesize, }
    output_profile = cog_profiles.get("deflate")

    with rasterio.Env():
        with MemoryFile() as memfile:
            with memfile.open(**params) as mem:
                with futures.ThreadPoolExecutor(max_workers=50) as executor:
                    future_work = [
                        executor.submit(
                            _call_tile_endpoint, tile, tiles_url, extrema,
                            tilesize) for tile in tiles]

                    for f in tqdm(futures.as_completed(future_work),
                                  total=len(future_work)):
                        pass

                for f in _filter_futures(future_work):
                    window, img = f
                    with rasterio.open(BytesIO(img.content)) as src_dst:
                        mem.write(
                            src_dst.read(indexes=(1, 2, 3)), window=window)

                cog_translate(
                    mem,
                    out_path,
                    output_profile,
                    config=dict(
                        GDAL_NUM_THREADS="ALL_CPUS",
                        GDAL_TIFF_OVR_BLOCKSIZE="128"),
                )


if __name__ == '__main__':
    main()
