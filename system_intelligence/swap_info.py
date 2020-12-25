"""Functions to query system's swap memory."""

import typing as t
import psutil
from rich import print
from .util.register_decorator import register

from .base_info import BaseInfo


@register
class SwapInfo(BaseInfo):
    """
    Info on swap memory
    """
    def __init__(self):
        super().__init__()
        self.SWAP = psutil is not None

    def query_swap(self) -> t.Optional[int]:
        """
        Get information about swap.
        """
        if not self.SWAP:
            return None
        total_swap = psutil.swap_memory().total

        return total_swap

    def print_swap_info(self, swap: int) -> None:
        """
        Print info about swap memory (total size)
        """
        print(f'[bold blue]Swap size: {str(swap)}')
