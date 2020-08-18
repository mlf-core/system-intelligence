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
    'mkl': ('python -c "import mkl; print(mkl.get_version_string())"', None),
    'java': ('-version', None),
    'ruby': (None, None),
    'mpirun': (None, None),
    'spack': (None, None)
}

PYTHON_PACKAGES = [
    'chainer', 'Cython', 'h5py', 'ipython', 'mpi4py', 'Nuitka', 'numba', 'numpy',
    'pandas', 'pycuda', 'pyopencl', 'scikit-learn', 'scipy', 'tensorflow', 'pytorch',
    'xgboost'
]


def _run_version_query(cmd, version_line=None) -> t.Optional[str]:
    shell_required = True if len(cmd) < 2 or isinstance(cmd, str) else False
    try:
        result, error = subprocess.Popen(cmd, universal_newlines=True, shell=shell_required,
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    except(subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return None
    except FileNotFoundError:
        return None
    version_raw = result
    if error and not version_raw:
        if 'Traceback' in error or 'Check the permissions and owner of that directory.' in error:
            version_raw, error = None, None
        else:
            # When automatically written to stderr -> e.g. java -version writes to stderr
            version_raw = error
    if not error and not version_raw:
        return None
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
    no_path_exceptions = ['mkl']
    software_info = {}
    for program, version_tuple in VERSION_QUERY_FLAGS.items():
        path = shutil.which(program)
        if path is None and program not in no_path_exceptions:
            continue
        if version_tuple[0] is None:
            version_flag = DEFAULT_VERSION_QUERY_FLAG
        else:
            version_flag = version_tuple[0]
        # The package cannot be found -> It must be one of the exceptions
        if not path:
            cmd = [version_flag]
        else:
            cmd = [program, version_flag]
        _LOG.debug(f'running "{cmd}"')
        version = _run_version_query(cmd, version_tuple[1])
        software_info[program] = {'path': path, 'version': version}

    # python packages
    py_packages = {}
    for package in PYTHON_PACKAGES:
        version = _run_version_query(f'python -m pip freeze | grep {package}')
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
        try:
            package_version = version['version'].split('==')[1]
        except IndexError:
            package_version = version['version']
        table.add_row(package, package_version)

    console.print(table)
