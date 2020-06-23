from rich.box import HEAVY_HEAD
from rich.style import Style
from rich.table import Table


def create_styled_table(title: str) -> Table:
    """
    Creates a custom rich styled table, which all outputs share.

    :return: rich styled table
    """
    return Table(title=f'[bold]{title}', title_style='red', header_style=Style(color="red", bold=True), box=HEAVY_HEAD)
