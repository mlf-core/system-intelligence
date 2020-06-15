"""Console script for system_intelligence."""
import os
import pathlib
import sys
import click

from system_intelligence.query import query_and_export

WD = os.path.dirname(__file__)


@click.command()
@click.argument('scope', type=click.Choice(['all', 'cpu', 'gpu', 'ram']), default='all')
@click.option('--format', type=click.Choice(['raw', 'json']), default='raw',
              help='output format')
@click.option('--target', type=str, default='stdout',
              help='Output file path. if \'stdout\' output is printed to the console.')
def main(scope, format, target):
    """
    Query your system for hardware and software related information.

    Currently supported arguments are 'all', 'cpu', 'gpu', 'ram'.
    """
    click.echo(click.style(r"""
                   _                       _       _       _ _ _
     ___ _   _ ___| |_ ___ _ __ ___       (_)_ __ | |_ ___| | (_) __ _  ___ _ __   ___ ___
    / __| | | / __| __/ _ \ '_ ` _ \ _____| | '_ \| __/ _ \ | | |/ _` |/ _ \ '_ \ / __/ _ \
    \__ \ |_| \__ \ ||  __/ | | | | |_____| | | | | ||  __/ | | | (_| |  __/ | | | (_|  __/
    |___/\__, |___/\__\___|_| |_| |_|     |_|_| |_|\__\___|_|_|_|\__, |\___|_| |_|\___\___|
          |___/                                                   |___/
    """, fg='red'))
    target = {
        'stdout': sys.stdout,
        'stderr': sys.stderr
    }.get(target, pathlib.Path(target))
    query_and_export(query_scope=scope, export_format=format, export_target=target)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
