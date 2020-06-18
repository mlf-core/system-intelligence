import typing as t

import psutil
from rich.console import Console

from system_intelligence.util.rich_util import create_styled_table


def query_network() -> t.Optional[int]:
    """Get information about swap."""

    return psutil.net_if_stats()


def print_network_info(network_info):
    table = create_styled_table('Network Information')

    table.add_column('Network Name', justify='left')
    table.add_column('Status', justify='left')
    table.add_column('Duplex', justify='left')
    table.add_column('Speed', justify='left')
    table.add_column('mtu', justify='left')

    for network, snicstats in network_info.items():
        table.add_row(network, str(snicstats.isup), str(snicstats.duplex), str(snicstats.speed), str(snicstats.mtu))

    console = Console()
    console.print(table)
