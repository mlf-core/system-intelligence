"""Query and export system data in one step."""

import json
import pathlib
import typing as t

from ruamel.yaml import YAML

from .cpu_info import query_cpu, print_cpu_info  # noqa F401
from .gpu_info import query_gpus, print_gpus_info  # noqa F401
from .hdd_info import print_hdd_info, query_hdd  # noqa F401
from .host_info import query_host, print_host_info  # noqa F401
from .network_info import query_network, print_network_info  # noqa F401
from .os_info import query_os, print_os_info  # noqa F401
from .ram_info import query_ram, print_ram_info  # noqa F401
from .software_info import query_software, print_software_info  # noqa F401
from .swap_info import query_swap, print_swap_info  # noqa F401


def query_and_export(query_scope: list, verbose: bool, export_format: str, output: t.Any, **kwargs):
    """Query the given scope of the system and export results in a given format to a given target."""
    info = query(query_scope, verbose, **kwargs)
    if output:
        output = pathlib.Path(output)
        export(info, export_format, output)


def query(query_scope: list, verbose: bool, **kwargs) -> t.Any:
    """Wrap around selected system query functions."""
    info = {'cpu': {},
            'gpus': {},
            'ram': {},
            'host': {},
            'os': {},
            'hdd': {},
            'swap': {},
            'network': {},
            'software': {}}
    if query_scope == ['all']:
        query_scope = ['host', 'os', 'network', 'cpu', 'gpus', 'ram', 'hdd', 'swap', 'software']

    for query in query_scope:
        get_info = f'query_{query}'
        query_info = globals()[get_info]()
        info[query] = query_info
        if verbose:
            print_info = f'print_{query}_info'
            globals()[print_info](query_info)

    return info


def export(info, export_format: str, export_target: t.Any):
    """Export information obtained by system query to a specified format."""
    if export_format == 'json':
        with open(str(export_target), 'w', encoding='utf-8') as json_file:
            json.dump(info, json_file, indent=2, ensure_ascii=False)
    elif export_format == 'raw':
        with open(str(export_target), 'a', encoding='utf-8') as text_file:
            text_file.write(str(info))
    elif export_format == 'yml':
        yaml = YAML(typ='safe')
        yaml.dump(info, export_target)
    else:
        raise NotImplementedError(f'format={export_format} target={export_target}')
