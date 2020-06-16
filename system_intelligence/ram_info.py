"""Functions to query system's RAM."""

import logging
import subprocess
import typing as t
from xml.etree import ElementTree as ET

import click
import xmltodict as xmltodict

from .available_features import psutil, RAM_TOTAL
from .util.dict_util import flatten
from .util.process_util import is_process_accessible

_LOG = logging.getLogger(__name__)


def query_ram_total() -> t.Optional[int]:
    """Get information about total available RAM."""
    if not RAM_TOTAL:
        return None
    return psutil.virtual_memory().total


def query_ram(sudo: bool = False, **kwargs) -> t.Mapping[str, t.Any]:
    """Get all available information about RAM."""
    total_ram = query_ram_total()
    ram_banks = query_ram_banks(sudo=sudo, **kwargs)
    ram: t.Dict[str, t.Any] = {'total': total_ram}
    if ram_banks:
        ram['banks'] = ram_banks
    return ram


def query_ram_banks(sudo: bool = False, **_) -> t.List[t.Mapping[str, t.Any]]:
    """Extract information about RAM dice installed in the system."""
    if not sudo:
        click.echo(click.style('Run system-intelligence with sudo to enable more verbose RAM output', fg='green'))
    if not is_process_accessible(['lshw']):
        click.echo(click.style('lshw is not installed! Unable to fetch detailed RAM information.', fg='yellow'))
    try:
        xml_root, xml_dict = parse_lshw(sudo=sudo)
        tmp = dict(xml_dict)['list']['node']
        # for el in tmp:
        #     print(flatten(el))
        #     print()
    except subprocess.TimeoutExpired:
        return []
    except subprocess.CalledProcessError:
        return []
    except FileNotFoundError:
        return []
    except ET.ParseError:
        return []
    nodes = xml_root.findall('.//node')
    _LOG.debug('%i nodes', len(nodes))
    ram_banks = []
    for node in nodes:
        node_id = node.attrib['id']
        _LOG.debug('%s', node_id)
        if not node_id.startswith('bank'):
            continue
        ram_banks.append(query_ram_bank(node))
    return ram_banks


def parse_lshw(sudo: bool = False):
    """Get RAM information via lshw."""
    cmd = (['sudo'] if sudo else []) + ['lshw', '-c', 'memory', '-xml', '-quiet']
    result = subprocess.run(cmd, timeout=5, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return ET.fromstring(result.stdout.decode()), xmltodict.parse(result.stdout.decode())


def query_ram_bank(node: ET.Element) -> t.Mapping[str, t.Any]:
    """Extract information about given RAM bank from XML node."""
    bank_size = node.findall('./size')
    bank_clock = node.findall('./clock')
    if len(bank_size) != 1 or len(bank_clock) != 1:
        _LOG.warning('there should be exactly one size and clock value for a bank'
                     ' but there are %i and %i respectively', len(bank_size), len(bank_clock))
    _LOG.debug(ET.tostring(node, encoding='utf8', method='xml').decode())
    assert bank_size[0].text is not None
    ram_bank = {'memory': int(bank_size[0].text)}
    try:
        if bank_clock[0].text is not None:
            ram_bank['clock'] = int(bank_clock[0].text)
    except IndexError:
        pass
    return ram_bank
