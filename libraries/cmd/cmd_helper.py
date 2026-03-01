#!/usr/bin/python3
"""Cmd Helper"""

import os
import subprocess

from libraries.context.context import Context
from libraries.logging.logging_helper import LoggingHelper


class CmdHelper:
    """Class to help usage of Cmd"""

    @staticmethod
    def run(
        cmd: str,
        shell=True,
        check=True,
        timeout=10*60,
        cwd=os.getcwd()
    ):
        """Run a command"""

        if Context.is_simulated():
            LoggingHelper.log_info(
                message=Context.get_text(
                    'run_cmd_simulation',
                    cmd=cmd,
                    shell=shell,
                    check=check
                )
            )
            return True

        try:
            subprocess.run(
                cmd,
                shell=shell,
                check=check,
                timeout=timeout
            )
        except subprocess.TimeoutExpired as exc:
            LoggingHelper.log_error(
                message=Context.get_text(
                    'error_cmd_timeout',
                    cmd=cmd,
                    timeout=str(timeout),
                    cwd=cwd
                ),
                exc=exc
            )
            return False

        return True

    @staticmethod
    def retrieve_cmd_result(
        read_cmd: str,
        timeout=10*60,
        cwd=os.getcwd()
    ):
        """Retrieve result from a read command"""

        result = None
        try:
            result = subprocess.run(
                read_cmd,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                timeout=timeout,
                cwd=cwd
            )
        except subprocess.TimeoutExpired as exc:
            LoggingHelper.log_error(
                message=Context.get_text(
                    'error_cmd_timeout',
                    cmd=read_cmd,
                    timeout=str(timeout)
                ),
                exc=exc
            )
            result = None

        return result
