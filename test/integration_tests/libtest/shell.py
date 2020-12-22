"""
Helper code for executing commands in a subshell (a real process running on
the machine) and interfacing with it.
"""
from contextlib import AbstractContextManager
from errno import EEXIST, ESRCH
from sarge import Command, Capture
from subprocess import PIPE  # nosec: This is used for testing only.
import sys


class Shell(AbstractContextManager):
    """
    A real shell process running on the host machine.
    This class is meant to be used as a context manager.
    """
    def __init__(self, shell_binary, return_code_echo_command,
                 command_separator):
        """
        Initialises the shell process wrapper. This call does not start the
        shell yet, only the access into the context does.
        """
        self._binary = shell_binary
        self._capture = Capture(timeout=0.1, buffer_size=-1)
        self._command = Command(shell_binary, stdout=self._capture)
        self._echo = return_code_echo_command + command_separator
        self._separator = command_separator
        self._started = False

    def __enter__(self):
        """
        Starts the shell.
        """
        return self.start()

    def __exit__(self, exc_type, exc_value, trace):
        """
        Leaves the shell.
        """
        self.terminate()
        return False

    def start(self):
        """
        Starts the underlying shell.
        """
        if self._started:
            raise OSError(EEXIST, "The shell is already running!")
        print("[Shell] Starting '{0}'...".format(self._binary),
              file=sys.stderr)
        try:
            self._command.run(input=PIPE, async_=True)
        except ValueError:
            raise FileNotFoundError("The shell binary '{0}' cannot be found "
                                    "on the system.".format(self._binary))
        self._started = True
        return self

    @property
    def pid(self):
        """
        :return: The PID of the running process, if running.
        """
        if not self._started:
            raise OSError(ESRCH, "The shell is not running!")
        return self._command.process.pid

    def kill(self):
        """
        Kills (signal 9) the underlying shell.
        """
        if not self._started:
            raise OSError(ESRCH, "The shell is not running!")
        self._command.kill()
        self._command.wait()
        self._capture.close(True)
        self._started = False

    def terminate(self):
        """
        Terminates (signal 15) the underlying shell.
        """
        if not self._started:
            raise OSError(ESRCH, "The shell is not running!")
        self._command.terminate()
        self._command.wait()
        self._capture.close(True)
        self._started = False

    def execute_command(self, cmd):
        """
        Executes the command in the shell.
        :return: A tuple of the result of the executed command, and the
        `stdout` of it.
        """
        cmd = cmd + self._separator
        print("[Shell '{0}'] Running command: {1}".format(self._binary, cmd),
              file=sys.stderr)

        self._command.stdin.write(cmd.encode('utf-8'))
        self._command.stdin.write(self._echo.encode('utf-8'))
        self._command.stdin.flush()

        stdout = self._capture.read(timeout=None)
        parts = stdout.decode().rstrip().split('\n')
        result, returncode = '\n'.join(parts[:-1]).rstrip(), parts[-1].rstrip()

        print("[Shell '{0}'] Command result {1}:\n{2}".
              format(self._binary, returncode, result), file=sys.stderr)
        return int(returncode), result
