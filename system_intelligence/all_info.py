import typing as t

from .cpu_info import query_cpu
from .gpu_info import query_gpus
from .hdd_info import query_hdd_model
from .host_info import query_host
from .network_info import query_network
from .os_info import query_os
from .ram_info import query_ram
from .software_info import query_software
from .swap_info import query_swap


def query_all(**kwargs) -> t.Mapping[str, t.Any]:
    """Get all available information about the system."""
    return {
        'host': query_host(),
        'os': query_os(),
        'software': query_software(),
        'cpu': query_cpu(**kwargs),
        'gpus': query_gpus(**kwargs),
        'ram': query_ram(**kwargs),
        'hdds': query_hdd_model(),
        'swap': query_swap(),
        'network': query_network()
        }
