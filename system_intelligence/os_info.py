import platform
from rich import print
from .util.register_decorator import register

from .base_info import BaseInfo


@register
class OsInfo(BaseInfo):
    """
    Print the users OS
    """

    def __init__(self):
        super().__init__()

    def query_os(self):
        """
        Get information about OS.
        """
        system = platform.platform()

        return system

    def print_os_info(self, system):
        print(f'[bold blue]{system}')
