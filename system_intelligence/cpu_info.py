"""Functions to query system's CPUs/APUs."""

import logging
import typing as t

from rich.console import Console
from rich.table import Table

from .available_features import cpuinfo, pint, psutil, CPU, CPU_CLOCK, CPU_CORES

_LOG = logging.getLogger(__name__)


def query_cpu_clock() -> t.Tuple[t.Optional[int], t.Optional[int], t.Optional[int]]:
    """Get current, minimum and maximum clock frequency of the CPU in the system."""
    if not CPU_CLOCK:
        return None, None, None
    try:
        cpu_clock = psutil.cpu_freq()
    except FileNotFoundError:
        return None, None, None
    if cpu_clock is None:
        return None, None, None
    return cpu_clock.current, cpu_clock.min, cpu_clock.max


def query_cpu_cores() -> t.Tuple[t.Optional[int], t.Optional[int]]:
    """Get number of logical and physical cores of the system's CPU."""
    if not CPU_CORES:
        return None, None
    return psutil.cpu_count(), psutil.cpu_count(logical=False)


def _get_cache_size(level: int, cpuinfo_data: dict) -> t.Optional[int]:
    """Get CPU cache size in bytes at a given level.

    If no units are provided, assume source data is in KiB.
    """
    raw_value = cpuinfo_data.get(f'l{level}_data_cache_size', cpuinfo_data.get(f'l{level}_cache_size', None))
    if raw_value is None:
        return None
    assert isinstance(raw_value, str), (type(raw_value), raw_value)
    # KB, MB: "this practice frequently leads to confusion and is deprecated"
    # see https://en.wikipedia.org/wiki/JEDEC_memory_standards
    if raw_value.endswith('KB'):
        raw_value = raw_value[:-2] + 'KiB'
    elif raw_value.endswith('MB'):
        raw_value = raw_value[:-2] + 'MiB'
    ureg = pint.UnitRegistry()
    value = ureg(raw_value)
    if isinstance(value, int):
        return value * 1024
    _LOG.debug('L%i cache size parsed by pint: "%s" -> %s', level, raw_value, value)
    value = value.to('bytes')
    return int(value.magnitude)


def _get_cache_sizes(cpuinfo_data: dict) -> t.Mapping[int, t.Optional[int]]:
    return {lvl: _get_cache_size(lvl, cpuinfo_data) for lvl in range(1, 4)}


def query_cpu(**_) -> t.Mapping[str, t.Any]:
    """Get information about CPU present in the system."""
    if not CPU:
        return {}
    cpu = cpuinfo.get_cpu_info()
    clock_current, clock_min, clock_max = query_cpu_clock()
    logical_cores, physical_cores = query_cpu_cores()
    cache = _get_cache_sizes(cpu)

    return {
        'vendor_id_raw': cpu.get('vendor_id_raw'),
        'hardware_raw': cpu.get('hardware_raw'),
        'brand_raw': cpu.get('brand_raw'),
        'arch': cpu.get('arch'),
        'logical_cores': str(logical_cores),
        'physical_cores': str(physical_cores),
        'clock': str(clock_current),
        'clock_min': str(clock_min),
        'clock_max': str(clock_max),
        'cache': str(cache)}


def print_cpu_info(cpu_info: dict) -> None:
    table = Table(title='CPU')

    table.add_column('Vendor ID', justify='left')
    table.add_column('Hardware', justify='left')
    table.add_column('Brand', justify='left')
    table.add_column('Architecture', justify='left')
    table.add_column('Logical Cores', justify='left')
    table.add_column('Physical Cores', justify='left')
    table.add_column('Clock', justify='left')
    table.add_column('Minimal Clock', justify='left')
    table.add_column('Maximal Clock', justify='left')
    table.add_column('Cache', justify='left')

    table.add_row(*cpu_info.values())

    console = Console()
    console.print(table)
