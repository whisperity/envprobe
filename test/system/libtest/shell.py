# Copyright (C) 2018 Whisperity
#
# SPDX-License-Identifier: GPL-3.0
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Helper code for executing commands in a subshell (a real process running on
the machine) and interfacing with it.
"""
from contextlib import AbstractContextManager
from errno import EEXIST, ESRCH
from sarge import Command, Capture
from subprocess import PIPE  # nosec: This is used for testing only.
import sys


class Shell(AbstractContextManager):
    """A real shell running on the host machine, to be used in a context."""
    def __init__(self, shell_binary, shell_argstr, return_code_echo_command,
                 command_separator, is_interactive):
        """Sets up the context for a system shell process.

        Parameters
        ----------
        shell_binary : str
            The shell binary, e.g. ``/bin/bash``, to start.
        shell_argstr : str
            Additional arguments to be passed to the shell at start.
        return_code_echo_command : str
            A command string in the shell's own language that prints to
            standard output the return code of the previously executed command.
        command_separator : str
            The character sequence to separate commands with.
        is_interactive : bool
            Whether the started shell is an interactive one.
            This does only change the behaviour of the context manager, to make
            the shell itself interactive, additional arguments in
            `shell_argstr` might need to be passed.
        """
        self._args = shell_argstr
        self._binary = shell_binary
        # Note: The execution of the command and the reading of the output
        # has to happen BEFORE this timeout is hit, but a large timeout would
        # also mean waiting a lot for small commands, so this has to be
        # balanced carefully.
        self._capture = Capture(timeout=0.1, buffer_size=-1)
        self._command = Command(shell_binary + ' ' + shell_argstr,
                                stdout=self._capture)
        self._echo = return_code_echo_command + command_separator
        self._interactive = is_interactive
        self._separator = command_separator
        self._started = False

    def __enter__(self):
        """Starts the shell in a context manager setting."""
        return self.start()

    def __exit__(self, exc_type, exc_value, trace):
        """Destroys the shell and leaves the context."""
        if self._interactive:
            self.kill()
        else:
            self.terminate()
        return False

    def start(self):
        """Starts the underlying shell process as configured in
        :py:func:`__init__`.
        """
        if self._started:
            raise OSError(EEXIST, "The shell is already running!")
        print("[Shell] Starting '{0} {1}'...".format(self._binary, self._args),
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
        """The PID of the started process."""
        if not self._started:
            raise OSError(ESRCH, "The shell is not running!")
        return self._command.process.pid

    def kill(self):
        """Kills (by sending ``SIGKILL`` (``9``)) to the shell process."""
        if not self._started:
            raise OSError(ESRCH, "The shell is not running!")
        self._command.kill()
        self._command.wait()
        self._capture.close(True)
        self._started = False

    def terminate(self):
        """Terminates (by sending ``SIGTERM`` (``15``)) to the shell process.

        Note
        ----
        Interactive shells (:py:attr:`is_interactive`) usually catch and ignore
        this signal, and as such, :py:func:`kill` should be used to shut them
        down properly.
        """
        if not self._started:
            raise OSError(ESRCH, "The shell is not running!")
        self._command.terminate()
        self._command.wait()
        self._capture.close(True)
        self._started = False

    def execute_command(self, cmd, timeout=None):
        """Execute `cmd` in the shell, wait `timeout` seconds, and read back
        the result.

        Parameters
        ----------
        cmd : str
            The command to execute.
            This string will be written into the shell's standard input
            verbatim.
        timeout : int
            The time (in seconds) to wait before the output of the command is
            read.

        Returns
        -------
        return_code : int
            The return code of the executed command.
        result : str
            The *standard output* of the executed command.

        Note
        ----
        The command executed in the shell is extended with
        :py:attr:`command_separator` and :py:attr:`return_code_echo_command`,
        and written to the shell.
        In case of a conventional ``/bin/bash`` shell, for example, executing
        `cmd` ``echo "Foo"`` will actually execute:

        .. code-block:: bash

           echo "Foo";
           echo $;

        Which will result in the output:

        .. code-block:: bash

           Foo
           0

        to be read as a result.

        Warning
        -------
        The underlying library and the execution of piped shells does not allow
        a good method of "sensing" when the output became available while
        keeping interactivity.
        A too small `timeout` on a loaded system might result in output being
        lost, while a too big one will result in every command waiting for
        a considerable time.
        """
        cmd = cmd + self._separator
        print("[Shell '{0}'] Running command: {1}".format(self._binary, cmd),
              file=sys.stderr)

        self._command.stdin.write(cmd.encode('utf-8'))
        self._command.stdin.write(self._echo.encode('utf-8'))
        self._command.stdin.flush()

        stdout = self._capture.read(timeout=timeout)
        parts = stdout.decode().rstrip().split('\n')
        result, returncode = '\n'.join(parts[:-1]).rstrip(), parts[-1].rstrip()

        print("[Shell '{0}'] Command result {1}:\n{2}".
              format(self._binary, returncode, result), file=sys.stderr)
        return int(returncode), result
