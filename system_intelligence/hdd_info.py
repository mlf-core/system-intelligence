import itertools
import os
import typing as t
import psutil
from rich import print

from .base_info import BaseInfo


class HddInfo(BaseInfo):
    """
    Provide any available info on HDDs on the users system
    """

    def __init__(self):
        super().__init__()
        self.IGNORED_DEVICE_PATHS = {'/dm', '/loop', '/md'}
        if self.OS == 'linux':
            import pyudev
            self.context = pyudev.Context()
        else:
            pyudev = None
            print('[bold yellow]Unable to import package pyudev. HDD information may be limited.')
        self.HDD = pyudev is not None

    def query_hdd(self):
        """
        Query info on any available HDDs on the users system
        """
        hdd_models = self.query_hdd_model()
        hdd_usage = self.query_hdd_usage()

        return {'model': hdd_models, 'usage': hdd_usage}

    def query_hdd_model(self) -> t.Dict[str, dict]:
        """
        Get information about all hard drives.
        """
        if not self.HDD:
            return {}
        hdds = {}
        for device in self.context.list_devices(subsystem='block', DEVTYPE='disk'):
            if any(_ in device.device_path for _ in self.IGNORED_DEVICE_PATHS):
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

    def query_hdd_usage(self) -> t.Dict[t.Any, t.Dict[str, str]]:
        """
        Query info on any HDD usage on the users system
        """
        hdd_to_usage = {}
        for part in psutil.disk_partitions(all=False):
            if os.name == 'nt':
                # skip cd-rom drives with no disk in it; they may raise ENOENT,
                # pop-up a Windows GUI error for a non-ready partition or just hang.
                if 'cdrom' in part.opts or part.fstype == '':
                    continue
            usage = psutil.disk_usage(part.mountpoint)
            hdd_to_usage[part.device] = {'total': self.format_bytes(usage.total),
                                         'used': self.format_bytes(usage.used),
                                         'free': self.format_bytes(usage.free),
                                         'percentage': str(usage.percent),
                                         'fstype': part.fstype,
                                         'mountpoint': part.mountpoint}

        return hdd_to_usage

    def print_hdd_info(self, hdd_info: dict) -> None:
        """
        Print info on any available HDDs on the users system
        """
        # Models
        self.init_table(title='Hard Disks Drives', column_names=['Disk Name', 'Model'])

        for hdd, details in hdd_info['model'].items():
            self.table.add_row(hdd, details['model'])

        self.print_table()

        # Usage
        self.init_table(title='Disk Usage', column_names=['Device', 'Total', 'Used', 'Free', 'Use %', 'Type', 'Mount'])

        for device, usage in hdd_info['usage'].items():
            self.table.add_row(device,
                               usage['total'],
                               usage['used'],
                               usage['free'],
                               usage['percentage'],
                               usage['fstype'],
                               usage['mountpoint'])

        self.print_table()
