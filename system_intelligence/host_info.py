import platform
from rich import print

from.base_info import BaseInfo


class HostInfo(BaseInfo):
    """
    Bla
    """
    def __init__(self):
        super().__init__()

    def query_host(self) -> str:
        """
        Get information about current host.
        """
        hostname = platform.node()

        return hostname

    def print_host_info(self, hostname):
        """
        Bla
        """
        print(f'[bold blue]Hostname: {hostname}')
