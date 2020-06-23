"""Functions to query presence of relevant software."""

import logging
import shutil
import subprocess
import typing as t

from rich.console import Console

from system_intelligence.util.rich_util import create_styled_table

_LOG = logging.getLogger(__name__)

DEFAULT_VERSION_QUERY_FLAG = '--version'

# Second argument is the version_tuple
# First element of the tuple is an overwrite version flag
# Second element of the tuple is an overwrite line number
VERSION_QUERY_FLAGS = {
    # compilers
    'gcc': (None, None),
    'g++': (None, None),
    'gfortran': (None, None),
    'clang': (None, None),
    'clang++': (None, None),
    'flang': (None, None),
    'pgcc': (None, None),
    'pgc++': (None, None),
    'pgfortran': (None, None),
    'icc': (None, None),
    'icpc': (None, None),
    'ifort': (None, None),
    'mpicc': (None, None),
    'mpic++': (None, None),
    'mpifort': (None, None),
    # python
    'python': (None, None),
    'pip': (None, None),
    # other
    'nvcc': (None, 3),  # CUDA
    'java': (None, None),
    'ruby': (None, None),
    'mpirun': (None, None),
    'spack': (None, None)
}

PYTHON_PACKAGES = [
    'chainer', 'Cython', 'h5py', 'ipython', 'mpi4py', 'Nuitka', 'numba', 'numpy',
    'pandas', 'pycuda', 'pyopencl', 'scikit-learn', 'scipy', 'tensorflow', 'pytorch'
]


def _run_version_query(cmd, version_line=None, **kwargs) -> t.Optional[str]:
    try:
        result = subprocess.run(
            cmd, timeout=5, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return None
    except FileNotFoundError:  # on Windows
        return None
    version_raw = result.stdout.decode()
    if not version_raw:
        version_raw = result.stderr.decode()
    try:
        if version_line:
            version = version_raw.splitlines()[version_line]
        else:
            version = version_raw.splitlines()[0]
    except IndexError:
        version = version_raw
    return version


def query_software():
    """Get information about relevant software."""
    software_info = {}
    for program, version_tuple in VERSION_QUERY_FLAGS.items():
        path = shutil.which(program)
        if path is None:
            continue
        if version_tuple[0] is None:
            version_flag = DEFAULT_VERSION_QUERY_FLAG
        cmd = [program, version_flag]
        _LOG.debug(f'running "{cmd}"')
        version = _run_version_query(cmd, version_tuple[1])
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

    table.add_column('Name', justify='left')
    table.add_column('Path', justify='left')
    table.add_column('Version', justify='left')

    for software_name, path_version in software_info.items():
        table.add_row(software_name, path_version['path'], path_version['version'])

    console = Console()
    console.print(table)

    table = create_styled_table('Python Packages')

    table.add_column('Name', justify='left')
    table.add_column('Version', justify='left')

    for package, version in software_info['python']['packages'].items():
        package_version = version['version'].split('==')[1]
        table.add_row(package, package_version)

    console.print(table)
