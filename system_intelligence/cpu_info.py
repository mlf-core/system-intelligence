import logging
import subprocess
import typing as t
from rich import print

from .base_info import BaseInfo

_LOG = logging.getLogger(__name__)


try:
    import cpuinfo
except ImportError:
    cpuinfo = None
    print('[bold yellow]Unable to import package cpuinfo. CPU information may be limited.')
except Exception:  # noqa E722
    # raise Exception("py-cpuinfo currently only works on X86 and some ARM CPUs.")
    cpuinfo = None  # pylint: disable = invalid-name
    print('[bold red]Package cpuinfo does not support this system!')

try:
    import pint
except ImportError:
    pint = None
    print('[bold yellow]Unable to import package pint. CPU information may be limited.')

try:
    import psutil
except ImportError:
    psutil = None
    print('[bold yellow]Unable to import package psutil. CPU and Network information may be limited.')


class CpuInfo(BaseInfo):
    """
    Info class to collect info about the CPU on the users operating system
    """

    def __init__(self):
        super().__init__()
        self.CPU = cpuinfo is not None and pint is not None
        self.CPU_CLOCK = psutil is not None
        self.CPU_CORES = psutil is not None

    def query_cpu(self, **_) -> t.Mapping[str, t.Any]:
        """
        Get information about CPU present in the system.
        """
        if not self.CPU:
            return {}
        cpu = cpuinfo.get_cpu_info()
        clock_current, clock_min, clock_max = self.query_cpu_clock()
        logical_cores, physical_cores = self.query_cpu_cores()
        cache = dict(self._get_cache_sizes(cpu))
        for level, hz in cache.items():
            cache[level] = hz

        return {
            'vendor_id_raw': cpu.get('vendor_id_raw'),
            'hardware_raw': cpu.get('hardware_raw') if self.OS == 'linux' else 'NA',
            'brand_raw': cpu.get('brand_raw'),
            'arch': cpu.get('arch'),
            'logical_cores': str(logical_cores),
            'physical_cores': str(physical_cores),
            'clock': f'{str(clock_current)} MHz',
            'clock_min': f'{str(clock_min)} MHz',
            'clock_max': f'{str(clock_max)} MHz',
            'cache': '\n'.join(f'L{cache_level}: {size}' for cache_level, size in cache.items())}

    def query_cpu_clock(self) -> t.Tuple[t.Optional[int], t.Optional[int], t.Optional[int]]:
        """
        Get current, minimum and maximum clock frequency of the CPU in the system.
        """
        if not self.CPU_CLOCK:
            return None, None, None
        try:
            cpu_clock = psutil.cpu_freq()
        except FileNotFoundError:
            return None, None, None
        if cpu_clock is None:
            return None, None, None
        return cpu_clock.current, cpu_clock.min, cpu_clock.max

    def query_cpu_cores(self) -> t.Tuple[t.Optional[int], t.Optional[int]]:
        """
        Get number of logical and physical cores of the system's CPU.
        """
        if not self.CPU_CORES:
            return None, None
        return psutil.cpu_count(), psutil.cpu_count(logical=False)

    def _get_cache_size(self, level: int, cpuinfo_data: dict) -> t.Optional[str]:
        """
        Get CPU cache size in bytes at a given level.
        """
        # L2 cache on MacOS is already included in cpuinfo data (required for L1 and L3)
        # L1i and L1d cache are summed up into one value for L1 cache
        cache_size = 0
        if self.OS == 'darwin' and level != 2:
            cmd = (['sysctl', 'hw'])
            result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            hw_cache_level = subprocess.check_output(('grep', f'l{level}'), stdin=result.stdout).decode('utf-8')
            # for each cache level part (basically only relevant for L1) get the total cache size
            for cache_level_part in hw_cache_level.split('\n')[:-1]:
                split_cache_parts = cache_level_part.split(':')
                cache_size += int(split_cache_parts[1])
        else:
            cache_size = cpuinfo_data.get(f'l{level}_data_cache_size', cpuinfo_data.get(f'l{level}_cache_size', None))
        # return cache size in nicely formatted bytes unit
        return self.format_bytes(cache_size, device='cpu_cache')

    def _get_cache_sizes(self, cpuinfo_data: dict) -> t.Mapping[int, t.Optional[int]]:
        """
        For each Cache Level (L1, L2 and L3) get the actual cache size
        """
        return {lvl: CpuInfo._get_cache_size(self, lvl, cpuinfo_data) for lvl in range(1, 4)}

    def print_cpu_info(self, cpu_info: dict) -> None:
        """
        Print all Infos available for CPUs for the users operating system
        """
        # Prettify cache
        cpu_info['cache'] = cpu_info['cache'].replace('{', '').replace('}', '')
        column_names = ['Vendor ID', 'Hardware', 'Brand', 'Architecture', 'Logical Cores', 'Physical Cores', 'Clock', 'Minimal Clock', 'Maximal Clock', 'Cache']
        self.init_table(title='Central Processing Unit', column_names=column_names)
        self.table.add_row(*cpu_info.values())
        self.print_table()
