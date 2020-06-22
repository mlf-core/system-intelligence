"""Functions to query the host."""

import platform

import click


def query_host() -> str:
    """Get information about current host."""
    hostname = platform.node()

    return hostname


def print_host_info(hostname):
    click.echo(click.style(f'Hostname: {hostname}', fg='blue'))
