from subprocess import Popen, PIPE

import click


def is_process_accessible(shell_command: list) -> bool:
    """
    Verifies that a shell command is accessible and in the PATH.
    :return: True if accessible, false if not
    """
    try:
        git_installed = Popen(shell_command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        (git_installed_stdout, git_installed_stderr) = git_installed.communicate()
        if git_installed.returncode != 0:
            click.echo(click.style(f'Could not find \'{shell_command[0]}\' in the PATH. Is it installed?', fg='red'))
            click.echo(click.style(f'Run command was: \'{"".join(shell_command)} \'', fg='red'))
            return False
    except Exception:
        click.echo(click.style(f'Could not find \'{shell_command[0]}\' in the PATH. Is it installed?', fg='red'))
        click.echo(click.style(f'Run command was: \'{"".join(shell_command)} \'', fg='red'))
        return False

    return True
