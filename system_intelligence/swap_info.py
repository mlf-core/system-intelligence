"""Functions to query system's swap memory."""

import typing as t

import click
import psutil

try:
    import pyudev

    pyudev.Context()
except ImportError:
    pyudev = None
    click.echo(click.style('Unable to import package pyudev. HDD information may be limited.', fg='yellow'))

SWAP = psutil is not None


def query_swap() -> t.Optional[int]:
    """Get information about swap."""
    if not SWAP:
        return None
    total_swap = psutil.swap_memory().total

    return total_swap


def print_swap_info(swap: int) -> None:
    click.echo(click.style(f'Swap size: {str(swap)}', fg='blue'))
