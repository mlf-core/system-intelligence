"""Functions to query the host."""

import platform

from rich import print


def query_host() -> str:
    """Get information about current host."""
    hostname = platform.node()

    return hostname


def print_host_info(hostname):
    print(f'[bold blue]Hostname: {hostname}')
