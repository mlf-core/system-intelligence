"""Functions to query system's swap memory."""

import typing as t
import psutil
from rich import print

from .base_info import BaseInfo


class SwapInfo(BaseInfo):
    """
    Bla
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
        Bla
        """
        print(f'[bold blue]Swap size: {str(swap)}')
