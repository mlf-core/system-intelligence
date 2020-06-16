"""Functions to query presence of relevant software."""

import logging
import shutil
import subprocess
import typing as t

from rich.console import Console

from system_intelligence.util.rich_util import create_styled_table

_LOG = logging.getLogger(__name__)

DEFAULT_VERSION_QUERY_FLAG = '--version'

# Second argument overrides the default_version_query flag
VERSION_QUERY_FLAGS = {
    # compilers
    'gcc': None,
    'g++': None,
    'gfortran': None,
    'clang': None,
    'clang++': None,
    'flang': None,
    'pgcc': None,
    'pgc++': None,
    'pgfortran': None,
    'icc': None,
    'icpc': None,
    'ifort': None,
    'mpicc': None,
    'mpic++': None,
    'mpifort': None,
    # python
    'python': None,
    'pip': None,
    # other
    'java': None,
    'ruby': None,
    'nvcc': None,
    'mpirun': None,
    'spack': None}

PYTHON_PACKAGES = [
    'chainer', 'Cython', 'h5py', 'ipython', 'mpi4py', 'Nuitka', 'numba', 'numpy',
    'pandas', 'pycuda', 'pyopencl', 'scikit-learn', 'scipy', 'tensorflow', 'pytorch']


def _run_version_query(cmd, **kwargs) -> t.Optional[str]:
    try:
        result = subprocess.run(
            cmd, timeout=5, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
    except subprocess.TimeoutExpired:
        return None
    except subprocess.CalledProcessError:
        return None
    except FileNotFoundError:  # on Windows
        return None
    version_raw = result.stdout.decode()
    if not version_raw:
        version_raw = result.stderr.decode()
    try:
        version = version_raw.splitlines()[0]
    except IndexError:
        version = version_raw
    return version


def query_software():
    """Get information about relevant software."""
    software_info = {}
    for program, flag in VERSION_QUERY_FLAGS.items():
        path = shutil.which(program)
        if path is None:
            continue
        if flag is None:
            flag = DEFAULT_VERSION_QUERY_FLAG
        cmd = [program, flag]
        _LOG.debug('running "%s"', cmd)
        version = _run_version_query(cmd)
        software_info[program] = {'path': path, 'version': version}

    # python packages
    py_packages = {}
    for package in PYTHON_PACKAGES:
        version = _run_version_query(
            f'python -m pip freeze | grep {package}', shell=True)
        if version is None:
            continue
        py_packages[package] = {'version': version}
    software_info['python']['packages'] = py_packages

    return software_info


def print_software_info(software_info: dict):
    table = create_styled_table('Installed Software')

    table.add_column('Software Name', justify='left')
    table.add_column('Path', justify='left')
    table.add_column('Version', justify='left')

    for software_name, path_version in software_info.items():
        table.add_row(software_name, path_version['path'], path_version['version'])

    console = Console()
    console.print(table)
