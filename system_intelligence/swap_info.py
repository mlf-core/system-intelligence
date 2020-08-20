"""Functions to query system's swap memory."""

import typing as t

import psutil

from rich import print

try:
    import pyudev

    pyudev.Context()
except ImportError:
    pyudev = None
    print('[bold yellow]Unable to import package pyudev. HDD information may be limited.')

SWAP = psutil is not None


def query_swap() -> t.Optional[int]:
    """Get information about swap."""
    if not SWAP:
        return None
    total_swap = psutil.swap_memory().total

    return total_swap


def print_swap_info(swap: int) -> None:
    print(f'[bold blue]Swap size: {str(swap)}')
