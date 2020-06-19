"""Probe the system for available features to determine what can be queried."""

import logging

import click

_LOG = logging.getLogger(__name__)

try:
    import cpuinfo
except ImportError:
    cpuinfo = None
    click.echo(click.style('Unable to import package cpuinfo. CPU information may be limited.', fg='yellow'))
except Exception:  # noqa E722
    # raise Exception("py-cpuinfo currently only works on X86 and some ARM CPUs.")
    cpuinfo = None  # pylint: disable = invalid-name
    click.echo(click.style('Package cpuinfo does not support this system!', fg='red'))

try:
    import pint
except ImportError:
    pint = None
    click.echo(click.style('Unable to import package pint. CPU information may be limited.', fg='yellow'))

CPU = cpuinfo is not None and pint is not None

try:
    import psutil
except ImportError:
    psutil = None
    click.echo(click.style('Unable to import package psutil. CPU and Network information may be limited.', fg='yellow'))

CPU_CLOCK = psutil is not None
CPU_CORES = psutil is not None

try:
    import pycuda
    import pycuda.driver as cuda
    import pycuda.autoinit

    _LOG.debug('using CUDA version %s', '.'.join(str(_) for _ in cuda.get_version()))
except ImportError:
    cuda = None
    click.echo(click.style('Unable to import package pycuda. GPU information may be limited.', fg='yellow'))
except pycuda._driver.Error:  # pylint: disable = protected-access
    cuda = None  # pylint: disable = invalid-name
    click.echo(click.style('Unable to initialize CUDA. CPU information may be limited.', fg='yellow'))

GPU = cuda is not None

try:
    import pyudev

    pyudev.Context()
except ImportError:
    pyudev = None
    click.echo(click.style('Unable to import package pyudev. HDD information may be limited.', fg='yellow'))

HDD = pyudev is not None
RAM_TOTAL = psutil is not None
SWAP = psutil is not None
