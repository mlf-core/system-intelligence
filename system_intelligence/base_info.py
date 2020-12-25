from rich.box import HEAVY_HEAD
from rich.style import Style
from rich.table import Table
from rich.console import Console
from sys import platform


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
