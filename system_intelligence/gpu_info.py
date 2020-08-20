"""Functions to query GPUs in the system."""

import typing as t

from rich.console import Console
from rich import print

from .util.rich_util import create_styled_table
from .util.unit_conversion_util import bytes_to_hreadable_string, hz_to_hreadable_string


class QueryError(RuntimeError):
    """Indicate that a query failed."""


compute_capability_to_architecture = {
    2: 'Fermi',
    3: 'Kepler',
    5: 'Maxwell',
    6: 'Pascal',
    7: 'Volta',
    8: 'Ampere'
}

try:
    import pycuda
    import pycuda.driver as cuda
    import pycuda.autoinit  # noqa F401
    is_CUDA_available = True
except (ModuleNotFoundError, ImportError):
    is_CUDA_available = False


def query_gpus(**_) -> t.List[t.Mapping[str, t.Any]]:
    """Get information about all GPUs."""
    if not is_CUDA_available:
        print('[bold yellow]Unable to import package pycuda. GPU information may be limited.')
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
            'compute_capability': str(float('.'.join(str(_) for _ in compute_capability))),
            'memory': bytes_to_hreadable_string(device.total_memory()),
            'memory_clock': hz_to_hreadable_string(attributes[cuda.device_attribute.MEMORY_CLOCK_RATE]),
            'clock': hz_to_hreadable_string(attributes[cuda.device_attribute.CLOCK_RATE]),
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


def print_gpus_info(gpus_info: list):
    table = create_styled_table('Graphical Processing Unit')

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
