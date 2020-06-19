import typing as t

import psutil
from rich.console import Console

from system_intelligence.util.rich_util import create_styled_table


def query_network() -> t.Dict[t.Any, t.Dict[str, str]]:
    """Get information about swap."""
    stats = psutil.net_if_stats()
    final_repr = {}
    for device, snicstats in stats.items():
        final_repr[device] = {'isup': str(snicstats.isup),
                              'duplex': str(snicstats.duplex),
                              'speed': str(snicstats.speed),
                              'mtu': str(snicstats.mtu)}

    return final_repr


def print_network_info(network_info):
    table = create_styled_table('Network Information')

    table.add_column('Network Name', justify='left')
    table.add_column('Status', justify='left')
    table.add_column('Duplex', justify='left')
    table.add_column('Speed', justify='left')
    table.add_column('mtu', justify='left')

    for network, snicstats in network_info.items():
        table.add_row(network,
                      snicstats['isup'],
                      snicstats['duplex'],
                      snicstats['speed'],
                      snicstats['mtu'])

    console = Console()
    console.print(table)
