"""
fill_mosaic_holes.py: Make sure all mosaics have the same keys
"""

import json
from pathlib import Path

import click


@click.command()
@click.option(
    '-o',
    '--out-dir',
    type=click.Path(dir_okay=True, file_okay=False, writable=True),
    help='Output directory for filled mosaics.')
@click.argument('input', nargs=-1, type=click.Path(exists=True))
def main(input, out_dir):
    """Fill mosaic holes using other mosaics.

    If a quadkey exists in one MosaicJSON input but not in another, the JSON
    with missing data will be filled by another mosaic where the key exists. If
    only one mosaic is passed as input, it will be unchanged since there are no
    other mosaics to fill from.

    The order of input paths is the same order used for filling values of
    missing keys from other mosaics.
    """
    mosaics = []
    for path in input:
        with open(path) as f:
            mosaics.append(json.load(f))

    mosaics = handle_mosaics(mosaics)
    for path, mosaic in zip(input, mosaics):
        Path(out_dir).mkdir(exist_ok=True, parents=True)
        with open(Path(out_dir) / Path(path).name, 'w') as f:
            json.dump(mosaic, f, separators=(',', ':'))


def handle_mosaics(mosaics):
    """Fill gaps in mosaics

    If a quadkey is missing in one mosaic but exists in others, fill it in.

    Args:
        - mosaics: should be ordered from newest to oldest, so that the newest
          imagery is filled in.
    """

    # Find all quadkeys
    quadkeys = set()
    for mosaic in mosaics:
        quadkeys.update(mosaic['tiles'].keys())

    for mosaic in mosaics:
        for quadkey in quadkeys:
            if quadkey in mosaic['tiles'].keys():
                continue

            # Find value in some other mosaic
            for m in mosaics:
                if quadkey in m['tiles'].keys():
                    mosaic['tiles'][quadkey] = m['tiles'][quadkey]

    # Make sure all mosaics have the same number of keys
    n_keys = []
    for mosaic in mosaics:
        n_keys.append(len(mosaic['tiles'].keys()))

    msg = 'mosaics have different numbers of quadkeys'
    assert all(x == n_keys[0] for x in n_keys), msg

    return mosaics


if __name__ == '__main__':
    main()
