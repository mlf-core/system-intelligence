"""Console script for system_intelligence."""
import os
import pathlib
import sys
import click

from rich.traceback import install
from system_intelligence.query import query_and_export

WD = os.path.dirname(__file__)


@click.command()
@click.argument('scope',
                type=click.Choice(['all', 'cpu', 'gpus', 'ram', 'software', 'host', 'os', 'hdd', 'swap', 'network']),
                nargs=-1)
@click.option('--verbose/--silent', default=False)
@click.option('-f', '--format', type=click.Choice(['raw', 'json', 'yml']), default='raw',
              help='output format')
@click.option('-o', '--output', type=str,
              help='Output file path.')
def main(scope, verbose, format, output):
    """
    Query your system for hardware and software related information.

    Currently supported arguments are
    'all', 'cpu', 'gpus', 'ram', 'software', 'host', 'os', 'hdd', 'swap', 'network'
    """
    click.echo(click.style(r"""
                   _                       _       _       _ _ _
     ___ _   _ ___| |_ ___ _ __ ___       (_)_ __ | |_ ___| | (_) __ _  ___ _ __   ___ ___
    / __| | | / __| __/ _ \ '_ ` _ \ _____| | '_ \| __/ _ \ | | |/ _` |/ _ \ '_ \ / __/ _ \
    \__ \ |_| \__ \ ||  __/ | | | | |_____| | | | | ||  __/ | | | (_| |  __/ | | | (_|  __/
    |___/\__, |___/\__\___|_| |_| |_|     |_|_| |_|\__\___|_|_|_|\__, |\___|_| |_|\___\___|
          |___/                                                   |___/
    """, fg='red'))

    if not scope:
        click.echo(click.style('Please choose a scope! Run ', fg='red')
                   + click.style('system-intelligence scope --help ', fg='green')
                   + click.style('for more information.', fg='red'))
        sys.exit(1)

    for query in scope:
        query_and_export(query_scope=query, verbose=verbose, export_format=format, output=output)


if __name__ == "__main__":
    install()
    sys.exit(main())  # pragma: no cover
