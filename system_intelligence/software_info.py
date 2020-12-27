import logging
import shutil
import subprocess
import typing as t

from .base_info import BaseInfo

_LOG = logging.getLogger(__name__)


class SoftwareInfo(BaseInfo):
    """
    Query info on software available on the users system
    """
    def __init__(self):
        super().__init__()
        self.DEFAULT_VERSION_QUERY_FLAG = '--version'

        # Value is the version_tuple, key the corresponding package or software
        # First element of the tuple is an overwrite version flag
        # Second element of the tuple is an overwrite line number
        self.VERSION_QUERY_FLAGS = {
            **dict.fromkeys(['gcc', 'g++', 'gfortran', 'clang', 'clang++', 'flang', 'pgcc', 'pgc++',
                             'pgfortran', 'icc', 'icpc', 'ifort', 'mpicc', 'mpic++',
                             'mpifort', 'python', 'pip', 'ruby', 'mpirun', 'spack'], (None, None)),
            'nvcc': (None, 3),  # CUDA
            'mkl': ('python -c "import mkl; print(mkl.get_version_string())"', None),
            'java': ('-version', None)
        }

        self.PYTHON_PACKAGES = {
            'chainer', 'Cython', 'h5py', 'ipython', 'mpi4py', 'Nuitka', 'numba', 'numpy',
            'pandas', 'pycuda', 'pyopencl', 'scikit-learn', 'scipy', 'tensorflow', 'pytorch',
            'xgboost'
        }

    def query_software(self):
        """
        Get information about relevant software.
        """
        no_path_exceptions = ['mkl']
        software_info = {}
        for program, version_tuple in self.VERSION_QUERY_FLAGS.items():
            path = shutil.which(program)
            if path is None and program not in no_path_exceptions:
                continue
            version_flag = version_tuple[0] if version_tuple[0] else self.DEFAULT_VERSION_QUERY_FLAG
            # The package cannot be found -> It must be one of the exceptions
            if not path:
                cmd = [version_flag]
            else:
                cmd = [program, version_flag]
            _LOG.debug(f'running "{cmd}"')
            version = SoftwareInfo._run_version_query(cmd, version_tuple[1])
            software_info[program] = {'path': path, 'version': version}

        # python packages
        self.query_python_packages(software_info)

        return software_info

    @staticmethod
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

    def query_python_packages(self, software_info: dict) -> None:
        """
        Query versions of the python packages (if installed)
        """
        py_packages = {}
        packages = subprocess.check_output(['python', '-m', 'pip', 'freeze']).decode('utf-8').split('\n')
        package_set = {package[0]: package[1] for package in [s.split("==") for s in packages] if len(package) == 2}
        for package in package_set.keys():
            if package in self.PYTHON_PACKAGES:
                version = package_set[package]
                py_packages[package] = {'version': version}
        software_info['python']['packages'] = py_packages

    def print_software_info(self, software_info: dict):
        """
        Print info of some software available on the users system
        """
        self.init_table(title='Installed Software', column_names=['Name', 'Path', 'Version'])

        for software_name, path_version in software_info.items():
            self.table.add_row(software_name, path_version['path'], path_version['version'])

        self.print_table()

        self.init_table(title='Python Packages', column_names=['Name', 'Version'])
        if software_info['python']['packages'].items():
            for package, version in software_info['python']['packages'].items():
                try:
                    package_version = version['version'].split('==')[1]
                except IndexError:
                    package_version = version['version']
                self.table.add_row(package, package_version)

            self.print_table()
