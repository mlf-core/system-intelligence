"""Functions to query system's hard drives."""

import itertools
import os
import typing as t

import psutil
from rich.console import Console
from rich import print

from .util.rich_util import create_styled_table
from .util.unit_conversion_util import bytes_to_hreadable_string

IGNORED_DEVICE_PATHS = {'/dm', '/loop', '/md'}

try:
    import pyudev

    pyudev.Context()
except ImportError:
    pyudev = None
    print('[bold yellow]Unable to import package pyudev. HDD information may be limited.')

HDD = pyudev is not None


def query_hdd():
    hdd_models = query_hdd_model()
    hdd_usage = query_hdd_usage()

    return {'model': hdd_models, 'usage': hdd_usage}


def query_hdd_model() -> t.Dict[str, dict]:
    """Get information about all hard drives."""
    if not HDD:
        return {}
    context = pyudev.Context()
    hdds = {}
    for device in context.list_devices(subsystem='block', DEVTYPE='disk'):
        if any(_ in device.device_path for _ in IGNORED_DEVICE_PATHS):
            continue
        hdd = {'size': device.attributes.asint('size')}
        for device_ in itertools.chain([device], device.ancestors):
            try:
                hdd['model'] = device_.attributes.asstring('model')
                break
            except KeyError:
                hdd['model'] = ''
        hdds[device.device_node] = hdd

    return hdds


def query_hdd_usage() -> t.Dict[t.Any, t.Dict[str, str]]:
    hdd_to_usage = {}
    for part in psutil.disk_partitions(all=False):
        if os.name == 'nt':
            # skip cd-rom drives with no disk in it; they may raise ENOENT,
            # pop-up a Windows GUI error for a non-ready partition or just hang.
            if 'cdrom' in part.opts or part.fstype == '':
                continue
        usage = psutil.disk_usage(part.mountpoint)
        hdd_to_usage[part.device] = {'total': bytes_to_hreadable_string(usage.total),
                                     'used': bytes_to_hreadable_string(usage.used),
                                     'free': bytes_to_hreadable_string(usage.free),
                                     'percentage': str(usage.percent),
                                     'fstype': part.fstype,
                                     'mountpoint': part.mountpoint}

    return hdd_to_usage


def print_hdd_info(hdd_info: dict) -> None:
    # Models
    table = create_styled_table('Hard Disks Drives')

    table.add_column('Disk Name', justify='left')
    table.add_column('Model', justify='left')

    for hdd, details in hdd_info['model'].items():
        table.add_row(hdd, details['model'])
        #  bytes_to_hreadable_string(details['size']) <- Removed since it may be misleading

    console = Console()
    console.print(table)

    # Usage
    table = create_styled_table('Disk Usage')

    table.add_column('Device', justify='left')
    table.add_column('Total', justify='left')
    table.add_column('Used', justify='left')
    table.add_column('Free', justify='left')
    table.add_column('Use %', justify='left')
    table.add_column('Type', justify='left')
    table.add_column('Mount', justify='left')

    for device, usage in hdd_info['usage'].items():
        table.add_row(device,
                      usage['total'],
                      usage['used'],
                      usage['free'],
                      usage['percentage'],
                      usage['fstype'],
                      usage['mountpoint'])

    console.print(table)
