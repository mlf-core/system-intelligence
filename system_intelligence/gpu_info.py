"""Functions to query GPUs in the system."""

import typing as t

from rich.box import HEAVY_HEAD
from rich.console import Console
from rich.style import Style
from rich.table import Table

from .available_features import cuda, GPU

from .errors import QueryError

compute_capability_to_architecture = {
    2: 'Fermi',
    3: 'Kepler',
    5: 'Maxwell',
    6: 'Pascal',
    7: 'Volta',
    8: 'Ampere'
}


def query_gpus(**_) -> t.List[t.Mapping[str, t.Any]]:
    """Get information about all GPUs."""
    if not GPU:
        return []
    gpus = []
    for i in range(cuda.Device.count()):
        device = cuda.Device(i)
        gpus.append(query_gpu(device))
    return gpus


def query_gpu(device: 'cuda.Device') -> t.Mapping[str, t.Any]:
    """Get information about a given GPU."""
    attributes = device.get_attributes()
    compute_capability = device.compute_capability()
    multiprocessors = attributes[cuda.device_attribute.MULTIPROCESSOR_COUNT]
    cuda_cores = calculate_cuda_cores(compute_capability, multiprocessors)
    try:
        return {
            'architecture': compute_capability_to_architecture[compute_capability[0]],
            'brand': device.name(),
            'memory': str(device.total_memory()),
            'memory_clock': str(attributes[cuda.device_attribute.MEMORY_CLOCK_RATE]),
            'compute_capability': str(float('.'.join(str(_) for _ in compute_capability))),
            'clock': str(attributes[cuda.device_attribute.CLOCK_RATE]),
            'multiprocessors': str(multiprocessors),
            'cores': str(cuda_cores),
            'warp_size': str(attributes[cuda.device_attribute.WARP_SIZE])
        }
    except KeyError as err:
        raise QueryError(f'expected value not present among device attributes: {device.get_attributes()}') from err


def calculate_cuda_cores(compute_capability: t.Tuple[int, int], multiprocessors: int) -> t.Optional[int]:
    """Calculate number of cuda cores according to Nvidia's specifications."""
    if compute_capability[0] == 2:  # Fermi
        if compute_capability[1] == 1:
            return multiprocessors * 48
        return multiprocessors * 32
    if compute_capability[0] == 3:  # Kepler
        return multiprocessors * 192
    if compute_capability[0] == 5:  # Maxwell
        return multiprocessors * 128
    if compute_capability[0] == 6:  # Pascal
        if compute_capability[1] == 0:
            return multiprocessors * 64
        if compute_capability[1] == 1:
            return multiprocessors * 128
    if compute_capability[0] == 7:  # Volta
        return multiprocessors * 64
    if compute_capability[0] == 8:  # Ampere
        return multiprocessors * 64
    return None


def print_gpu_info(gpus_info: list):
    table = Table(title='[bold]Graphical Processing Unit', title_style='red', header_style=Style(color="red", bold=True), box=HEAVY_HEAD)

    table.add_column('Architecture', justify='left')
    table.add_column('Brand', justify='left')
    table.add_column('Compute Capability', justify='left')
    table.add_column('Memory', justify='left')
    table.add_column('Memory Clock', justify='left')
    table.add_column('Clock', justify='left')
    table.add_column('Multiprocessors', justify='left')
    table.add_column('Cores', justify='left')
    table.add_column('Warp Size', justify='left')

    for gpu in gpus_info:
        table.add_row(*gpu.values())

    console = Console()
    console.print(table)
