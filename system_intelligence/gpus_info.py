import typing as t
from rich import print

from .base_info import BaseInfo


class QueryError(RuntimeError):
    """
    Indicate that a query failed.
    """


try:
    import pycuda
    import pycuda.driver as cuda
    import pycuda.autoinit  # noqa F401
    is_CUDA_available = True
except (ModuleNotFoundError, ImportError):
    is_CUDA_available = False


class GpusInfo(BaseInfo):
    """
    Query any info on GPUs available for the users system (currently only supports NVIDIA GPUs)
    """
    def __init__(self):
        super().__init__()
        self.compute_capability_to_architecture = {
            2: 'Fermi',
            3: 'Kepler',
            5: 'Maxwell',
            6: 'Pascal',
            7: 'Volta',
            8: 'Ampere'
        }

    def query_gpus(self, **_) -> t.List[t.Mapping[str, t.Any]]:
        """
        Get information about all GPUs.
        """
        if not is_CUDA_available:
            print('[bold yellow]Unable to import package pycuda. GPU information may be limited.')
            return []

        gpus = []
        for i in range(cuda.Device.count()):
            device = cuda.Device(i)
            gpus.append(self.query_gpu(device))

        return gpus

    def query_gpu(self, device: 'cuda.Device') -> t.Mapping[str, t.Any]:
        """
        Get information about a given GPU.
        """
        attributes = device.get_attributes()
        compute_capability = device.compute_capability()
        multiprocessors = attributes[cuda.device_attribute.MULTIPROCESSOR_COUNT]
        cuda_cores = GpusInfo.calculate_cuda_cores(compute_capability, multiprocessors)
        try:
            try:
                compute_cap_arch = self.compute_capability_to_architecture[compute_capability[0]]
            # compute capability in case its not implemented in SI yet
            except KeyError:
                compute_cap_arch = "Unknown"
            return {
                'architecture': compute_cap_arch,
                'brand': device.name(),
                'compute_capability': str(float('.'.join(str(_) for _ in compute_capability))),
                'memory': GpusInfo.format_bytes(self, device.total_memory()),
                'memory_clock': GpusInfo.hz_to_hreadable_string(attributes[cuda.device_attribute.MEMORY_CLOCK_RATE]),
                'clock': GpusInfo.hz_to_hreadable_string(attributes[cuda.device_attribute.CLOCK_RATE]),
                'multiprocessors': str(multiprocessors),
                'cores': str(cuda_cores),
                'warp_size': str(attributes[cuda.device_attribute.WARP_SIZE])
            }
        except KeyError as err:
            raise QueryError(f'expected value not present among device attributes: {device.get_attributes()}') from err

    @staticmethod
    def calculate_cuda_cores(compute_capability: t.Tuple[int, int], multiprocessors: int) -> t.Optional[int]:
        """
        Calculate number of cuda cores according to Nvidia's specifications.
        """
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

    def print_gpus_info(self, gpus_info: list):
        """
        Print info on any GPUs on the users system
        """
        if gpus_info:
            column_names = ['Architecture', 'Brand', 'Compute Capability', 'Memory', 'Memory Clock', 'Clock', 'Multiprocessors', 'Cores', 'Warp Size']
            self.init_table(title='Graphical Processing Unit', column_names=column_names)
            for gpu in gpus_info:
                self.table.add_row(*gpu.values())

            self.print_table()
