import json
import os
from copy import deepcopy
from functools import partial
from multiprocessing import Pool
from pathlib import Path

import click
import mercantile
from rasterio.rio import options
from rio_cogeo.profiles import cog_profiles

from cogeo_mosaic.mosaic import MosaicJSON
from cogeo_mosaic.overviews import create_low_level_cogs


@click.group()
def main():
    pass


@click.command()
@click.option(
    '-o',
    '--outdir',
    type=click.Path(dir_okay=True, file_okay=False, writable=True),
    help='Output directory for mosaics')
@click.option(
    '-z',
    '--overview-zoom',
    type=int,
    help='Overview zoom level',
    default=6,
    show_default=True)
@click.option(
    '--prefix', default='', required=False, help='Prefix for output Mosaics')
@click.argument('mosaic', type=click.File())
def split_mosaic(outdir, overview_zoom, mosaic, prefix):
    """Split full mosaic into overview mercator-aligned mosaics
    """
    # Input mosaic is an opened file
    mosaic = json.load(mosaic)

    outdir = Path(outdir)
    outdir.mkdir(exist_ok=True, parents=True)

    quadkeys = list(mosaic['tiles'].keys())

    overview_quadkeys = {qk[:overview_zoom] for qk in quadkeys}

    for overview_qk in overview_quadkeys:
        overview_mosaic = subset_mosaic(mosaic, overview_qk, overview_zoom)
        out_path = outdir / f'{prefix}{overview_qk}.json'

        with open(out_path, 'w') as f:
            json.dump(overview_mosaic.dict(exclude_none=True), f)


def subset_mosaic(mosaic, overview_qk, overview_zoom):
    """Create subset of mosaic within a single overview quadkey

    Args:
        - overview_qk: zoom 6 quadkey
    """
    qk_tiles = {
        k: v
        for k, v in mosaic['tiles'].items()
        if k[:overview_zoom] == overview_qk}
    bounds = mercantile.bounds(mercantile.quadkey_to_tile(overview_qk))

    # The new mosaic needs to be the same minzoom, quadkey zoom as
    new_mosaic = deepcopy(mosaic)
    new_mosaic['tiles'] = qk_tiles
    new_mosaic['bounds'] = bounds
    return MosaicJSON(**new_mosaic)


@click.command()
@click.argument("input_dir", type=click.Path())
# @click.option('-o', '--out-dir', type=click.Path(), help='Output dir')
@click.option(
    '-j', '--n-proc', type=int, default=4, help='# of processes in pool')
@click.option(
    "--cog-profile",
    "-p",
    type=click.Choice(cog_profiles.keys()),
    default="deflate",
    help="Cloud Optimized GeoTIFF profile (default: deflate).",
)
@click.option(
    "--overview-level",
    type=int,
    default=6,
    help="Max internal overivew level for the COG. "
    f"Will be used to get the size of each COG. Default is {256 * 2 **6}",
)
@options.creation_options
def create_overviews(
        input_dir, n_proc, cog_profile, overview_level, creation_options):

    files = [x for x in Path(input_dir).iterdir() if x.suffix == '.json']

    output_profile = cog_profiles.get(cog_profile)
    output_profile.update(dict(BIGTIFF=os.getenv("BIGTIFF", "IF_SAFER")))
    if creation_options:
        output_profile.update(creation_options)

    config = dict(
        GDAL_NUM_THREADS="ALL_CPU",
        GDAL_TIFF_INTERNAL_MASK=os.getenv("GDAL_TIFF_INTERNAL_MASK", True),
        GDAL_TIFF_OVR_BLOCKSIZE="128",
    )

    _create_overview = partial(
        create_overview,
        output_profile=output_profile,
        config=config,
        overview_level=overview_level)

    with Pool(n_proc) as p:
        p.map(_create_overview, files)


def create_overview(file, output_profile, config, overview_level):
    create_low_level_cogs(
        str(file),
        output_profile=output_profile,
        prefix=Path(file).stem,
        max_overview_level=overview_level,
        config=config,
        threads=1,
    )


main.add_command(split_mosaic)
main.add_command(create_overviews)

if __name__ == '__main__':
    main()
