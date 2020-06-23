"""Console script for system_intelligence."""
import sys
import click

from rich.traceback import install
from system_intelligence.query import query_and_export


@click.command()
@click.argument('scope',
                type=click.Choice(['all', 'cpu', 'gpus', 'ram', 'software', 'host', 'os', 'hdd', 'swap', 'network']),
                nargs=-1)
@click.option('--verbose/--silent', default=True)
@click.option('-f', '--output_format', type=click.Choice(['raw', 'json', 'yml']), default='raw',
              help='output format')
@click.option('-o', '--output', type=str,
              help='Output file path.')
def main(scope, verbose, output_format, output):
    """
    Query your system for hardware and software related information.

    Currently supported arguments are

    'all', 'cpu', 'gpus', 'ram', 'host', 'os', 'hdd', 'swap', 'network', 'software'
    """
    click.echo(click.style(r"""
                   _                       _       _       _ _ _
     ___ _   _ ___| |_ ___ _ __ ___       (_)_ __ | |_ ___| | (_) __ _  ___ _ __   ___ ___
    / __| | | / __| __/ _ \ '_ ` _ \ _____| | '_ \| __/ _ \ | | |/ _` |/ _ \ '_ \ / __/ _ \
    \__ \ |_| \__ \ ||  __/ | | | | |_____| | | | | ||  __/ | | | (_| |  __/ | | | (_|  __/
    |___/\__, |___/\__\___|_| |_| |_|     |_|_| |_|\__\___|_|_|_|\__, |\___|_| |_|\___\___|
          |___/                                                   |___/
    """, fg='blue'))

    if not verbose and not output:
        click.echo(click.style('Please specify an output path or run'
                               ' system-intelligence without the silent option!', fg='yellow'))
        sys.exit(1)

    if not scope:
        click.echo(click.style('Please choose a scope! Run ', fg='red')
                   + click.style('system-intelligence scope --help ', fg='green')
                   + click.style('for more information.', fg='red'))
        sys.exit(1)

    query_and_export(query_scope=list(scope), verbose=verbose, export_format=output_format, output=output)


if __name__ == "__main__":
    install()  # Install rich traceback
    sys.exit(main())  # pragma: no cover
