import logging
import os
import subprocess
import typing as t
from xml.etree import ElementTree as ET
import psutil
from rich import print

from .base_info import BaseInfo
from .util.process_util import is_process_accessible
from .util.unit_conversion_util import bytes_to_hreadable_string, hz_to_hreadable_string

_LOG = logging.getLogger(__name__)

try:
    import pyudev

    pyudev.Context()
except ImportError:
    pyudev = None
    print('[bold yellow]Unable to import package pyudev. RAM information may be limited.')


class RamInfo(BaseInfo):
    """
    Bla
    """

    def __init__(self):
        super().__init__()
        self.RAM_TOTAL = psutil is not None

    def query_ram(self, sudo: bool = False, **kwargs) -> t.Mapping[str, t.Any]:
        """
        Get all available information about RAM.
        """
        total_ram = self.query_ram_total()
        ram_banks, ram_cache = self.query_ram_banks_cache(sudo=sudo, **kwargs)
        ram: t.Dict[str, t.Any] = {'total': total_ram, 'banks': {}, 'cache': {}}
        if ram_banks:
            ram['banks'] = ram_banks
        if ram_cache:
            ram['cache'] = ram_cache

        return ram

    def query_ram_total(self) -> t.Optional[int]:
        """
        Get information about total available RAM.
        """
        if not self.RAM_TOTAL:
            return None

        return psutil.virtual_memory().total

    def query_ram_banks_cache(self, sudo: bool = False, **_) \
        -> t.Tuple[t.List[t.Mapping[str, t.Any]], t.List[t.Mapping[str, t.Any]]]:
        """
        Extract information about RAM dice installed in the system.
        """
        if os.geteuid() != 0:
            print('[bold green]Run system-intelligence with administrative permissions' +
                  ' to enable more verbose (bank and cache) RAM output!')
        if not is_process_accessible(['lshw']):
            print('[bold yellow]lshw is not installed! Unable to fetch detailed RAM information.')
        try:
            xml_root = self.parse_lshw(sudo=sudo)
        except subprocess.TimeoutExpired:
            return [], []
        except subprocess.CalledProcessError:
            return [], []
        except FileNotFoundError:
            return [], []
        except ET.ParseError:
            return [], []
        nodes = xml_root.findall('.//node')
        _LOG.debug(f'{len(nodes)} nodes')

        ram_banks = []
        ram_cache = []
        RAM_accessible = True
        for node in nodes:
            node_id = node.attrib['id']
            _LOG.debug(f'{node_id}')
            if node_id.startswith('bank'):
                bank_res = self.query_ram_bank(node)
                ram_banks.append(bank_res[0])
                RAM_accessible = bank_res[1]
            elif node_id.startswith('cache'):
                ram_cache.append(self.query_ram_cache(node))

        if not RAM_accessible:
            print('[bold yellow]Unable to fetch detailed RAM information. RAM is not accessible.')

        return ram_banks, ram_cache

    def parse_lshw(self, sudo: bool = False):
        """
        Get RAM information via lshw.
        """
        cmd = (['sudo'] if sudo else []) + ['lshw', '-c', 'memory', '-xml', '-quiet']
        result = subprocess.run(cmd, timeout=5, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return ET.fromstring(result.stdout.decode())

    def query_ram_bank(self, node: ET.Element) -> t.Tuple[t.Mapping[str, t.Any], bool]:
        """
        Extract information about given RAM bank from XML node.
        """
        RAM_accessible = True
        ram_bank = {'product': '',
                    'vendor': '',
                    'serial': '',
                    'description': '',
                    'slot': '',
                    'clock': '',
                    'size': ''}
        try:
            bank_product = node.findall('./product')
            ram_bank['product'] = bank_product[0].text
            bank_vendor = node.findall('./vendor')
            ram_bank['vendor'] = bank_vendor[0].text
            bank_serial = node.findall('./serial')
            ram_bank['serial'] = bank_serial[0].text
            bank_description = node.findall('./description')
            ram_bank['description'] = bank_description[0].text
            bank_slot = node.findall('./slot')
            ram_bank['slot'] = bank_slot[0].text
        except IndexError:
            RAM_accessible = False

        bank_size = node.findall('./size')
        bank_clock = node.findall('./clock')
        # if len(bank_size) != 1 or len(bank_clock) != 1:
        #     print(f'[bold yellow]there should be exactly one size and clock value for a bank but there are'
        #                            f' {len(bank_size)} and {len(bank_clock)} respectively')
        ram_bank['memory'] = bank_size[0].text
        try:
            if bank_clock[0].text is not None:
                ram_bank['clock'] = bank_clock[0].text
        except IndexError:
            pass

        return ram_bank, RAM_accessible

    def query_ram_cache(self, node: ET.Element) -> t.Mapping[str, t.Any]:
        """
        Bla
        """
        ram_cache = {'slot': 'NA', 'physid': 'NA', 'capacity': 'NA'}
        cache_slot = node.findall('./slot')
        ram_cache['slot'] = cache_slot[0].text
        cache_physid = node.findall('./physid')
        ram_cache['physid'] = cache_physid[0].text
        cache_capacity = node.findall('./capacity')
        ram_cache['capacity'] = cache_capacity[0].text

        return ram_cache

    def print_ram_info(self, ram_info: dict):
        """
        Bla
        """
        # Not run with sudo -> only total memory accessible
        if os.geteuid() != 0:
            self.init_table(title='Random Access Memory', column_names=['Total Memory'])

            self.table.add_row(f'{bytes_to_hreadable_string(ram_info["total"])}')

            self.print_table()
        else:
            column_names = ['Product', 'Serial', 'Vendor', 'Description', 'Slot', 'Memory / Memory Total', 'Clock']
            self.init_table(title='Random Access Memory Banks', column_names=column_names)

            for bank in ram_info['banks']:
                self.table.add_row(bank['product'],
                                   bank['serial'],
                                   bank['vendor'],
                                   bank['description'],
                                   bank['slot'],
                                   f'{bytes_to_hreadable_string(bank["memory"])} /'
                                   f'{bytes_to_hreadable_string(ram_info["total"])}',
                                   hz_to_hreadable_string(bank['clock']))
            self.print_table()

            self.init_table(title='Random-Access Memory Cache', column_names=['Slot', 'Physid', 'Capacity'])

            for cache in ram_info['cache']:
                self.table.add_row(cache['slot'], cache['physid'], bytes_to_hreadable_string(cache['capacity']))

            self.print_table()
