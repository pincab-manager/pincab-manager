#!/usr/bin/python3
"""Dialog to wait for a process"""

import threading
import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from libraries.constants.constants import Constants
from libraries.context.context import Context
from libraries.logging.logging_helper import LoggingHelper
from libraries.ui.ui_helper import UIHelper

# pylint: disable=attribute-defined-outside-init


class WaitingDialog:
    """Dialog to wait for a process"""

    def __init__(
        self,
        parent,
        process_name: str,
        process_function: any
    ):
        """Initialize dialog"""

        self.__process_name = process_name
        self.__process_function = process_function
        self.__interruption_requested = False

        # Create dialog
        self.__dialog = tk.Toplevel(parent)

        # Fix dialog's title
        self.__dialog.title(
            Context.get_text(
                'waiting'
            )
        )

        # Fix dialog's size and position
        UIHelper.center_dialog(
            dialog=self.__dialog,
            width=320,
            height=80
        )

        # Add a label with a progress bar
        waiting_label = tk.Label(
            self.__dialog,
            text=Context.get_text(
                'waiting_for',
                process=self.__process_name)
        )
        waiting_label.pack(
            fill=tk.X,
            padx=Constants.UI_PAD_BIG,
            pady=Constants.UI_PAD_BIG
        )

        self.__transform_progress = ttk.Progressbar(
            self.__dialog,
            mode='indeterminate'
        )
        self.__transform_progress.pack(
            fill=tk.X,
            padx=Constants.UI_PAD_BIG,
            pady=Constants.UI_PAD_BIG
        )
        self.__transform_progress.start(10)

        # Run process in a Thread to avoid blocking UI
        threading.Thread(
            target=self.__run_process,
            daemon=True
        ).start()

        # Bind closing event
        self.__dialog.protocol("WM_DELETE_WINDOW", self.__on_close)

    def __run_process(self):
        """Run process"""

        # Waiting 0.1 seconde to see the dialog if the process is quick
        time.sleep(0.1)

        # Waiting for the process
        try:
            self.__process_function(
                self.should_interrupt
            )
        except Exception as exc:
            LoggingHelper.log_error(
                message=Context.get_text(
                    'error_unknown'
                ),
                exc=exc
            )
            messagebox.showerror(
                title=Context.get_text('error_title'),
                message=Context.get_text('error_message'),
                parent=self.__dialog
            )

        # Close the dialog after process
        UIHelper.close_dialog(self.__dialog)

    def should_interrupt(self):
        """Return True if interruption has been requested"""
        return self.__interruption_requested

    def __on_close(self):
        """Called when closing"""

        # Ask if interrupt
        if messagebox.askyesno(
            Context.get_text('question'),
            Context.get_text('question_interrupt_process'),
            parent=self.__dialog
        ):
            self.__interruption_requested = True
