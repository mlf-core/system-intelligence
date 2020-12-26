from rich.box import HEAVY_HEAD
from rich.style import Style
from rich.table import Table
from rich.console import Console
from sys import platform
import typing as t


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
        Print the result table
        """
        self.console = Console()
        self.console.print(self.table)

    @staticmethod
    def format_bytes(size: t.Union[str, int]):
        """
        Format an integer representing a byte value into a nicer format.
        Examples:
            512 = 512 B
            123456 = 1MB
        """
        power = 2 ** 10
        n = 0
        power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
        # No result
        if not size or size == 'NA':
            return ''

        if isinstance(size, str):
            size = int(size)
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

        if isinstance(hz, str):
            hz = int(hz)
        i = 0
        while hz >= 1000 and i < len(suffixes) - 1:
            hz /= 1000.
            i += 1
        f = ('%.2f' % hz).rstrip('0').rstrip('.')

        return f'{f} {suffixes[i]}'
