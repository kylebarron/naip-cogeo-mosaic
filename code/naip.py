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
    help='Start imagery year, from 2011-2017')
@click.option(
    '-e',
    '--end-year',
    type=int,
    required=True,
    help='End imagery year, from 2011-2017')
@click.option(
    '--select-method',
    type=click.Choice(['first', 'last'], case_sensitive=False),
    required=False,
    default='last',
    show_default=True,
    help='image selection method')
@click.argument('manifest', type=click.File())
def manifest(start_year, end_year, select_method, manifest):
    """Select TIF URLs from manifest

    All states were photographed between 2011-2013, and again in 2014-2015. All
    states except Maine were photographed in 2016-2017.
    """
    if not 2011 <= start_year <= 2017:
        raise ValueError('start_year must be between 2011-2017')
    if not 2011 <= end_year <= 2017:
        raise ValueError('end_year must be between 2011-2017')

    lines = []
    for line in manifest:
        if line != 'manifest.test\n':
            lines.append(line.strip())

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

    # (al, 2011) -> al/2011
    match_strs = ['/'.join(c) for c in combos]
    matched_lines = [
        l for l in lines
        if l.endswith('.tif') and any(l.startswith(s) for s in match_strs)]

    for l in matched_lines:
        print(l)


if __name__ == '__main__':
    main()
