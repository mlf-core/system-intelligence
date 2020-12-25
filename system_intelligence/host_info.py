import platform
from rich import print
from .util.register_decorator import register

from.base_info import BaseInfo


@register
class HostInfo(BaseInfo):
    """
    Print host info
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
        Print users hostname
        """
        print(f'[bold blue]Hostname: {hostname}')
