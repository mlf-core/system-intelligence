from rich.box import HEAVY_HEAD
from rich.style import Style
from rich.table import Table
from rich.console import Console
from sys import platform
import typing as t
import csv
import os.path


class BaseInfo:
    """
    Hold basic operations shared between all device info classes
    """
    def __init__(self):
        self.OS = platform
        self.table = None
        self.console = None
        self.table_title = ''
        self.col_names = []

    def init_table(self, title: str, column_names):
        """
        Initialize the table; so create it and init the column names
        """
        self.create_styled_table(title)
        self.prepare_table(column_names)

    def create_styled_table(self, title: str) -> None:
        """
        Creates a custom rich styled table, which all outputs share.
        """
        self.table_title = title
        self.table = Table(title=f'[bold]{self.table_title}', title_style='red', header_style=Style(color="red", bold=True), box=HEAVY_HEAD)

    def prepare_table(self, column_names):
        """
        Add the specified column names to the table
        """
        self.col_names = column_names
        for name in column_names:
            self.table.add_column(name, justify='left')

    def print_table(self):
        """
        Print the result table to stdout
        """
        self.console = Console()
        self.console.print(self.table)

    def format_bytes(self, size: t.Union[str, int], device: str = ''):
        """
        Format an integer representing a byte value into a nicer format.
        Depending on the users system, formatting is done either using base10 conversion (Ubuntu and MacOS)
        or base2 (Windows and most other Linux distros).
        Examples:
            512 = 512 B
            123456 = 1MB
        """
        power = self.determine_base_conversion_factor(device)
        n = 0
        # if OS uses base10 conversion, use base10 units
        if power == 1000:
            power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
        # if OS uses base2 conversion, use SI units
        else:
            power_labels = {0: '', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
        # No result
        if not size or size == 'NA':
            return ''

        if isinstance(size, str):
            # on some systems and linux distros, some of the values may be pre-formatted (like 128 KiB)
            # therefore, they don't need to be casted and formatted
            try:
                size = int(size)
            except ValueError:
                return size
        while size >= power and n < len(power_labels) - 1:
            size /= power
            n += 1
        return f"{('%.2f' % size).rstrip('0').rstrip('.')} {power_labels[n]}B"

    @staticmethod
    def hz_to_hreadable_string(hz: int) -> str:
        """
        Transforms hertz into a human readable string with attached appropriate unit

        :param: number of hertz
        :return: human readable formatted string of hertz with unit
        """
        suffixes = ['Hz', 'kHz', 'MHz', 'GHz']

        # No result
        if not hz or hz == 'NA':
            return ''
        # on some systems and linux distros, some of the values may be pre-formatted (like 128 MHZ)
        # therefore, they don't need to be casted and formatted
        if isinstance(hz, str):
            try:
                hz = int(hz)
            except ValueError:
                return hz
        i = 0
        while hz >= 1000 and i < len(suffixes) - 1:
            hz /= 1000.
            i += 1
        f = ('%.2f' % hz).rstrip('0').rstrip('.')

        return f'{f} {suffixes[i]}'

    def determine_base_conversion_factor(self, device: str) -> int:
        """
        MacOS and Linux Ubuntu (disk storage) are using base10 unit conversion when it comes to some sort of storage (like file sizes or memory size)
        Most other OS (Linux distros and Windows) are using base2 instead.

        So to convert bytes to other units (like KB or KiB), base10 will use a factor of 1000 where base2 will use a factor of 1024!
        """
        if self.OS == 'linux' and not device:
            # this file stores some OS release details in most linux distros
            if os.path.isfile('/etc/os-release'):
                os_data = {}
                with open('/etc/os-release') as f:
                    reader = csv.reader(f, delimiter="=")
                    for row in reader:
                        if row:
                            os_data[row[0]] = row[1]
                # Linux Ubuntu uses base10 conversion
                if os_data['NAME'].lower() == "ubuntu":
                    return 1000
        # MacOS uses base10 conversion as well
        elif self.OS == 'darwin':
            return 1000
        # if the user os isn't either Linux Ubuntu nor MacOS use base2 conversion
        return 1024
