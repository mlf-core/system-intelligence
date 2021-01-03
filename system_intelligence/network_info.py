import typing as t
import psutil

from .base_info import BaseInfo


class NetworkInfo(BaseInfo):
    """
    Query some network info
    """

    def __init__(self):
        super().__init__()

    def query_network(self) -> t.Dict[t.Any, t.Dict[str, str]]:
        """
        Get information about network.
        """
        stats = psutil.net_if_stats()
        final_repr = {}
        for device, snicstats in stats.items():
            final_repr[device] = {'isup': str(snicstats.isup),
                                  'duplex': str(snicstats.duplex),
                                  'speed': str(snicstats.speed),
                                  'mtu': str(snicstats.mtu)}

        return final_repr

    def print_network_info(self, network_info):
        """
        Print the network info
        """
        self.init_table(title='Network Information', column_names=['Network Name', 'Status', 'Duplex', 'Speed', 'mtu'])

        for network, snicstats in network_info.items():
            self.table.add_row(network,
                               snicstats['isup'],
                               snicstats['duplex'],
                               snicstats['speed'],
                               snicstats['mtu'])

        self.print_table()
