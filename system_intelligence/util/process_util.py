from subprocess import Popen, PIPE


def is_process_accessible(shell_command: list) -> bool:
    """
    Verifies that a shell command is accessible and in the PATH.
    :return: True if accessible, false if not
    """
    try:
        is_command_installed = Popen(shell_command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        (git_installed_stdout, git_installed_stderr) = is_command_installed.communicate()
        if is_command_installed.returncode != 0:
            print(f'[bold red]Could not find \'{shell_command[0]}\' in the PATH. Is it installed?')
            print(f'Run command was: \'{"".join(shell_command)} \'')
            return False
    except Exception:
        print(f'[bold red]Could not find \'{shell_command[0]}\' in the PATH. Is it installed?')
        print(f'Run command was: \'{"".join(shell_command)} \'')
        return False

    return True
