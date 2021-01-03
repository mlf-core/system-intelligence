import typing as t
import psutil
from rich import print

from .base_info import BaseInfo


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
        swap_mem = self.format_bytes(swap)
        print(f'[bold blue]Swap size: {swap_mem if swap_mem else "NA"}')
