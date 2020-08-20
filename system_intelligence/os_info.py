"""Functions to query the operating system."""

import platform

from rich import print


def query_os():
    """Get information about OS."""
    # distro = distro.linux_distribution(full_distribution_name=False)
    system = platform.platform()  # + ' ' + ' '.join(str(_) for _ in distro)}

    return system


def print_os_info(system):
    print(f'[bold blue]{system}')
