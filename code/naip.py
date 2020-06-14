"""
Work with NAIP imagery and metadata
"""
import click


@click.group()
def main():
    pass


@main.command()
@click.option(
    '-s',
    '--start-year',
    type=int,
    required=True,
    help='Start imagery year, from 2011-2018')
@click.option(
    '-e',
    '--end-year',
    type=int,
    required=True,
    help='End imagery year, from 2011-2018')
@click.option(
    '--select-method',
    type=click.Choice(['first', 'last'], case_sensitive=False),
    required=False,
    default='last',
    show_default=True,
    help='image selection method')
@click.argument('file', type=click.File())
def manifest(start_year, end_year, select_method, file):
    """Select TIF URLs from manifest

    All states were photographed between 2011-2013, and again in 2014-2015. All
    states except Maine were photographed in 2016-2017. All states except Oregon
    were photographed in 2017-2018.
    """
    if not 2011 <= start_year <= 2018:
        raise ValueError('start_year must be between 2011-2018')
    if not 2011 <= end_year <= 2018:
        raise ValueError('end_year must be between 2011-2018')

    skip_lines = ['manifest.txt', 'readme.html', 'readme.txt']
    lines = []
    for line in file:
        line = line.strip()

        if line in skip_lines:
            continue

        lines.append(line)

    state_years = {}
    for line in lines:
        state, year = line.split('/')[:2]
        state_years[state] = state_years.get(state, set())
        state_years[state].add(int(year))

    # (state_abbr, year)
    combos = []
    for state, years in state_years.items():
        match_years = [y for y in years if start_year <= y <= end_year]
        if match_years:
            if select_method == 'first':
                combos.append((state, str(min(match_years))))
            elif select_method == 'last':
                combos.append((state, str(max(match_years))))
            else:
                raise ValueError('invalid select_method')

    # (al, 2011) -> al/2011
    match_strs = ['/'.join(c) for c in combos]
    matched_lines = [
        l for l in lines
        if l.endswith('.tif') and any(l.startswith(s) for s in match_strs)]

    # Deduplicate
    for l in deduplicate_urls(lines=matched_lines, select_method=select_method):
        print(l)


def deduplicate_urls(lines, select_method):
    """Deduplicate urls by cell

    Often, cells on state borders are duplicated across years. For example, this tile is duplicated in both Texas's and Louisiana's datasets:

    tx/2012/100cm/rgb/29093/m_2909302_ne_15_1_20120522.tif
    la/2013/100cm/rgb/29093/m_2909302_ne_15_1_20130702.tif

    As you can tell by the cell and name, these are the same position across
    different years. I deduplicate these to reduce load on the lambda function
    parsing the mosaicJSON.
    """
    # block: (year, url)
    data = {}
    for line in lines:
        block_id = name_to_id(line)
        year = name_to_year(line)

        existing = data.get(block_id)
        if existing is None:
            # Not a duplicate; add and continue
            data[block_id] = (year, line)
            continue

        # A duplicate; check whether to replace existing
        existing_year = existing[0]
        if select_method == 'last':
            if year > existing_year:
                data[block_id] = (year, line)
            continue

        elif select_method == 'first':
            if year < existing_year:
                data[block_id] = (year, line)
            continue

        else:
            raise ValueError('invalid select_method')

    return [t[1] for t in data.values()]


def name_to_year(s):
    return int(s.split('/')[1])


def name_to_id(s):
    """Generate block identifier from url string

    Example input:

    al/2013/100cm/rgb/30085/m_3008501_ne_16_1_20130928.tif
    """
    # cell: 30085
    # stem: m_3008501_ne_16_1_20130928.tif
    cell, stem = s.split('/')[4:]

    # Keep text before date
    # m_3008501_ne_16_1_
    stem = stem[:18]

    # Concatenate
    return f'{cell}/{stem}'


if __name__ == '__main__':
    main()
