"""Tests for setup scripts."""

import importlib
import itertools
import pathlib
import runpy
import subprocess
import sys
import types
import typing as t


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
