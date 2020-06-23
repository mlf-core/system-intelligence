"""Functions to query the operating system."""

import platform

import click


def query_os():
    """Get information about OS."""
    # distro = distro.linux_distribution(full_distribution_name=False)
    system = platform.platform()  # + ' ' + ' '.join(str(_) for _ in distro)}

    return system


def print_os_info(system):
    click.echo(click.style(system, fg='blue'))
