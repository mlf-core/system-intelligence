"""Console script for system_intelligence."""
import argparse
import os
import pathlib
import sys
import click

from system_intelligence.query import query_and_export

WD = os.path.dirname(__file__)


def main(args=None, namespace=None):
    """Run the command-line interface.
    Execute query_and_export() function according to the arguments.
    """
    click.echo(click.style(r"""
                   _                       _       _       _ _ _
     ___ _   _ ___| |_ ___ _ __ ___       (_)_ __ | |_ ___| | (_) __ _  ___ _ __   ___ ___
    / __| | | / __| __/ _ \ '_ ` _ \ _____| | '_ \| __/ _ \ | | |/ _` |/ _ \ '_ \ / __/ _ \
    \__ \ |_| \__ \ ||  __/ | | | | |_____| | | | | ||  __/ | | | (_| |  __/ | | | (_|  __/
    |___/\__, |___/\__\___|_| |_| |_|     |_|_| |_|\__\___|_|_|_|\__, |\___|_| |_|\___\___|
          |___/                                                   |___/
    """))

    parser = argparse.ArgumentParser(
        prog='system_query', description='''Comprehensive and concise system information tool.
        Query a given hardware and/or softawre scope of your system and get results in human-
        and machine-readable formats.''',
        epilog='''Copyright 2017-2020 by the contributors, Apache License 2.0,
        https://github.com/mbdevpl/system-query''',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, allow_abbrev=True)
    parser.add_argument(
        '-s', '--scope', type=str, default='all', choices=['all', 'cpu', 'gpu', 'ram'],
        help='''Scope of the query''')
    parser.add_argument(
        '-f', '--format', type=str, default='raw', choices=['raw', 'json'],
        help='''Format of the results of the query.''')
    parser.add_argument(
        '-t', '--target', type=str, default='stdout',
        help='''File path where to write the results of the query. Special values: "stdout"
        and "stderr" to write to stdout and stderr, respectively.''')

    args = parser.parse_args(args=args, namespace=namespace)
    target = {
        'stdout': sys.stdout,
        'stderr': sys.stderr
        }.get(args.target, pathlib.Path(args.target))
    query_and_export(query_scope=args.scope, export_format=args.format, export_target=target)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
