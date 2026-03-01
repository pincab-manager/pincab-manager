#!/usr/bin/python3
"""Logging Helper"""

import logging
import os
import tkinter as tk

from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

from libraries.context.context import Context


class LoggingHelper:
    """Class to help usage of logging"""

    __error_logger: logging.Logger = None
    __warning_logger: logging.Logger = None
    __info_logger: logging.Logger = None
    __log_ui: tk.Text = None

    @staticmethod
    def __init_info_logger():
        """Initialize __info_logger"""

        # Create the logs directory if it doesn't exist
        if not os.path.exists(Context.get_logs_path()):
            os.makedirs(Context.get_logs_path())

        # Get the current date to use in log file names
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Setup the logger for INFO level with format like 2024-09-28_info.log
        LoggingHelper.__info_logger = logging.getLogger('info_logger')
        LoggingHelper.__info_logger.setLevel(logging.INFO)
        info_handler = TimedRotatingFileHandler(
            f'{Context.get_logs_path()}/{current_date}_info.log',
            when='midnight',
            interval=1,
            backupCount=30
        )
        info_handler.suffix = "%Y-%m-%d"  # Suffix for rotating logs with the date
        info_handler.setLevel(logging.INFO)
        info_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        info_handler.setFormatter(info_formatter)
        LoggingHelper.__info_logger.addHandler(info_handler)

    @staticmethod
    def __init_warning_logger():
        """Initialize __warning_logger"""

        # Create the logs directory if it doesn't exist
        if not os.path.exists(Context.get_logs_path()):
            os.makedirs(Context.get_logs_path())

        # Get the current date to use in log file names
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Setup the logger for WARNING level with format like 2024-09-28_warning.log
        LoggingHelper.__warning_logger = logging.getLogger('warning_logger')
        LoggingHelper.__warning_logger.setLevel(logging.WARNING)
        warning_handler = TimedRotatingFileHandler(
            f'{Context.get_logs_path()}/{current_date}_warning.log',
            when='midnight',
            interval=1,
            backupCount=30
        )
        warning_handler.suffix = "%Y-%m-%d"  # Suffix for rotating logs with the date
        warning_handler.setLevel(logging.WARNING)
        warning_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        warning_handler.setFormatter(warning_formatter)
        LoggingHelper.__warning_logger.addHandler(warning_handler)

    @staticmethod
    def __init_error_logger():
        """Initialize __error_logger"""

        # Create the logs directory if it doesn't exist
        if not os.path.exists(Context.get_logs_path()):
            os.makedirs(Context.get_logs_path())

        # Get the current date to use in log file names
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Setup the logger for ERROR level with format like 2024-09-28_error.log
        LoggingHelper.__error_logger = logging.getLogger('error_logger')
        LoggingHelper.__error_logger.setLevel(logging.ERROR)
        error_handler = TimedRotatingFileHandler(
            f'{Context.get_logs_path()}/{current_date}_error.log',
            when='midnight',
            interval=1,
            backupCount=30
        )
        error_handler.suffix = "%Y-%m-%d"  # Suffix for rotating logs with the date
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        error_handler.setFormatter(error_formatter)
        LoggingHelper.__error_logger.addHandler(error_handler)

    @staticmethod
    def set_log_ui(log_ui: tk.Text):
        """Set a UI tk.Text to show log"""

        LoggingHelper.__log_ui = log_ui

    @staticmethod
    def log_info(message):
        """Log an informational message"""

        if LoggingHelper.__info_logger is None:
            LoggingHelper.__init_info_logger()

        if LoggingHelper.__log_ui is not None:
            LoggingHelper.__log_ui.config(state=tk.NORMAL)
            LoggingHelper.__log_ui.insert(tk.END, f'\n{message}\n')
            LoggingHelper.__log_ui.config(state=tk.DISABLED)
            LoggingHelper.__log_ui.see('end')

        LoggingHelper.__info_logger.info(message)

    @staticmethod
    def log_warning(message):
        """Log a warning message"""

        if LoggingHelper.__warning_logger is None:
            LoggingHelper.__init_warning_logger()

        if LoggingHelper.__log_ui is not None:
            LoggingHelper.__log_ui.config(state=tk.NORMAL)
            LoggingHelper.__log_ui.insert(tk.END, f'\n{message}\n')
            LoggingHelper.__log_ui.config(state=tk.DISABLED)
            LoggingHelper.__log_ui.see('end')

        LoggingHelper.__warning_logger.warning(message)

    @staticmethod
    def log_error(message, exc):
        """Log an error with its stack trace"""

        if LoggingHelper.__error_logger is None:
            LoggingHelper.__init_error_logger()

        if LoggingHelper.__log_ui is not None:
            LoggingHelper.__log_ui.config(state=tk.NORMAL)
            LoggingHelper.__log_ui.insert(tk.END, f'\n{message}\n')
            LoggingHelper.__log_ui.config(state=tk.DISABLED)
            LoggingHelper.__log_ui.see('end')

        LoggingHelper.__error_logger.error(message, exc_info=exc)
