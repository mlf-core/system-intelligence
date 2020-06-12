"""Tests for setup scripts."""

import importlib
import itertools
import os
import pathlib
import runpy
import subprocess
import sys
import types
import typing as t
import unittest


def run_program(*args, glob: bool = False):
    """Run subprocess with given args. Use path globbing for each arg that contains an asterisk."""
    if glob:
        cwd = pathlib.Path.cwd()
        args = tuple(itertools.chain.from_iterable(
            list(str(_.relative_to(cwd)) for _ in cwd.glob(arg)) if '*' in arg else [arg]
            for arg in args))
    process = subprocess.Popen(args)
    process.wait()
    if process.returncode != 0:
        raise AssertionError(f'execution of {args} returned {process.returncode}')
    return process


def run_pip(*args, **kwargs):
    python_exec_name = pathlib.Path(sys.executable).name
    pip_exec_name = python_exec_name.replace('python', 'pip')
    run_program(pip_exec_name, *args, **kwargs)


def run_module(name: str, *args, run_name: str = '__main__') -> None:
    backup_sys_argv = sys.argv
    sys.argv = [name + '.py'] + list(args)
    runpy.run_module(name, run_name=run_name)
    sys.argv = backup_sys_argv


def import_module(name: str = 'setup') -> types.ModuleType:
    setup_module = importlib.import_module(name)
    return setup_module


def import_module_member(module_name: str, member_name: str) -> t.Any:
    module = import_module(module_name)
    return getattr(module, member_name)


def get_package_folder_name():
    """Attempt to guess the built package name."""
    cwd = pathlib.Path.cwd()
    directories = [
        path for path in cwd.iterdir() if pathlib.Path(cwd, path).is_dir()
        and pathlib.Path(cwd, path, '__init__.py').is_file() and path.name != 'test']
    assert len(directories) == 2, directories
    return directories[0].name


@unittest.skipUnless(os.environ.get('TEST_PACKAGING') or os.environ.get('CI'), 'skipping packaging tests for actual package')
class IntergrationTests(unittest.TestCase):
    """Test if the boilerplate can actually create a valid package."""
    pkg_name = get_package_folder_name()

    def test_build_binary(self):
        run_module('setup', 'bdist')
        self.assertTrue(os.path.isdir('dist'))

    def test_build_wheel(self):
        run_module('setup', 'bdist_wheel')
        self.assertTrue(os.path.isdir('dist'))

    def test_build_source(self):
        run_module('setup', 'sdist', '--formats=gztar,zip')
        self.assertTrue(os.path.isdir('dist'))

    def test_install_code(self):
        run_pip('install', '.')
        run_pip('uninstall', '-y', self.pkg_name)

    def test_pip_error(self):
        with self.assertRaises(AssertionError):
            run_pip('wrong_pip_command')

    def test_setup_do_nothing_or_error(self):
        run_module('setup', 'wrong_setup_command', run_name='__not_main__')
        with self.assertRaises(SystemExit):
            run_module('setup', 'wrong_setup_command')
