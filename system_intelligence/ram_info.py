import logging
import os
import subprocess
import typing as t
from xml.etree import ElementTree as ET
import psutil
from rich import print

from .base_info import BaseInfo
from .util.process_util import is_process_accessible

_LOG = logging.getLogger(__name__)


class RamInfo(BaseInfo):
    """
    Get info on RAM
    """

    def __init__(self):
        super().__init__()
        self.RAM_TOTAL = psutil is not None
        # the pyudev package is only available for linux, so just import if the current OS is linux
        if self.OS == 'linux':
            import pyudev
            pyudev.Context()
        else:
            print('[bold yellow]Unable to import package pyudev. RAM information may be limited.')

    def query_ram(self, sudo: bool = False, **kwargs) -> t.Mapping[str, t.Any]:
        """
        Get all available information about RAM.
        """
        total_ram = self.query_ram_total()
        ram: t.Dict[str, t.Any] = {'total': total_ram, 'banks': {}}

        # query ram info for MacOS
        if self.OS == 'darwin':
            self.query_ram_macos(ram)
        elif self.OS == 'win32':
            self.query_ram_windows(ram)
        else:
            ram_banks, ram_cache = self.query_ram_banks_cache(sudo=sudo, **kwargs)
            ram['cache'] = {}
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

    def query_ram_macos(self, ram: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        """
        Query RAM info on MacOS
        """
        cmd = (['system_profiler', 'SPMemoryDataType'])
        ram_info = subprocess.check_output(cmd).decode('utf-8')
        # split the BANKs (like "slots") into different items
        ram_banks = [attribute.strip() for attribute in ram_info.split('BANK') if attribute][1:]

        # for each RAM slot extract details
        for i in range(0, len(ram_banks)):
            ram_slot_details = [attribute.strip() for attribute in ram_banks[i].split('\n') if attribute]
            ram_slot_details_set = {attribute_detail.split(':')[0].strip(): attribute_detail.split(':')[1].strip() for attribute_detail in ram_slot_details}
            ram['banks']['BANK ' + ram_slot_details[0]] = {attribute: value for attribute, value in ram_slot_details_set.items() if attribute in
                                                           {'Size', 'Type', 'Speed', 'Serial Number'}}
        return ram

    def query_ram_windows(self, ram: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        """
        Query RAM info under windows
        """
        cmd = (['wmic', 'MemoryChip', 'get', 'BankLabel,', 'Capacity,' 'Description,', 'Manufacturer,', 'Speed', '/format:csv'])
        # get ram info as a "csv" like string
        ram_info_csv = subprocess.check_output(cmd).strip().decode()
        # replace newline and carriage returns by splitting into lines
        # first line of the resulting list are the attributes names, so slice it off
        ram_info_stripped = [line for line in ram_info_csv.splitlines() if line][1:]
        # for each RAM slot, add info into ram dict
        for slot in ram_info_stripped:
            # the attributes values are comma separated, so split them; order is as follows
            # 1. Node, 2. BankLabel, 3. Capacity (in bytes), 4. Description, 5. Manufacturer, 6. Speed (in HZ)
            slot_attributes = slot.split(',')
            bank_name = slot_attributes[1]
            ram['banks'][bank_name] = {k: v for k, v in zip(['Capacity', 'Description', 'Manufacturer', 'Speed'], slot_attributes[2:])}
        return ram

    def query_ram_banks_cache(self, sudo: bool = False, **_) -> t.Tuple[t.List[t.Mapping[str, t.Any]], t.List[t.Mapping[str, t.Any]]]:
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
        ram_bank['memory'] = bank_size[0].text
        try:
            if bank_clock[0].text is not None:
                ram_bank['clock'] = bank_clock[0].text
        except IndexError:
            pass

        return ram_bank, RAM_accessible

    def query_ram_cache(self, node: ET.Element) -> t.Mapping[str, t.Any]:
        """
        Query info on RAM cache (currently only available for linux)
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
        Print all available RAM info for the users operating system
        """
        # run on MacOS
        if self.OS == 'darwin':
            column_names = ['Slot', 'Type', 'Size', 'Speed', 'Serial Number']
            self.init_table(title='Random Access Memory Banks', column_names=column_names)
            for ram_bank_id in ram_info['banks']:
                details = ram_info['banks'][ram_bank_id]
                self.table.add_row(ram_bank_id,
                                   details['Type'],
                                   details['Size'],
                                   details['Speed'],
                                   details['Serial Number'])
            self.print_table()
            self.print_total_memory(ram_info["total"])

        # run on windows
        elif self.OS == 'win32':
            column_names = ['Slot', 'Capacity', 'Description', 'Manufacturer', 'Speed']
            self.init_table(title='Random Access Memory Banks', column_names=column_names)
            for ram_bank_slot in ram_info['banks']:
                details = ram_info['banks'][ram_bank_slot]
                self.table.add_row(ram_bank_slot,
                                   self.format_bytes(details['Capacity']),
                                   details['Description'],
                                   details['Manufacturer'],
                                   self.hz_to_hreadable_string(details['Speed']))
            self.print_table()
            self.print_total_memory(ram_info['total'])

        # run on linux
        elif self.OS == 'linux':
            if os.geteuid() != 0:
                self.print_total_memory(ram_info['total'])
            else:
                column_names = ['Product', 'Serial', 'Vendor', 'Description', 'Slot', 'Memory / Memory Total', 'Clock']
                self.init_table(title='Random Access Memory Banks', column_names=column_names)

                for bank in ram_info['banks']:
                    self.table.add_row(bank['product'],
                                       bank['serial'],
                                       bank['vendor'],
                                       bank['description'],
                                       bank['slot'],
                                       f'{self.format_bytes(bank["memory"], device="ram")} /'
                                       f'{self.format_bytes(ram_info["total"], device="ram")}',
                                       RamInfo.hz_to_hreadable_string(bank['clock']))
                self.print_table()

                self.init_table(title='Random-Access Memory Cache', column_names=['Slot', 'Physid', 'Capacity'])

                for cache in ram_info['cache']:
                    self.table.add_row(cache['slot'], cache['physid'], self.format_bytes(cache['capacity']))
                self.print_table()

    def print_total_memory(self, ram_info_total: str) -> None:
        """
        Print the total memory table
        """
        self.init_table(title='Random Access Memory', column_names=['Total Memory'])
        self.table.add_row(f'{self.format_bytes(ram_info_total, device="ram")}')
        self.print_table()
