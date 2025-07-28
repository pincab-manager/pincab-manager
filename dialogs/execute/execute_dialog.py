#!/usr/bin/python3
"""Dialog to execute in the application"""

import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from executor.bdd_tables.bdd_tables_executor import BDDTablesExecutor
from executor.playlists.playlists_executor import PlaylistsExecutor
from executor.tables.tables_executor import TablesExecutor
from executor.configs.configs_executor import ConfigsExecutor
from libraries.constants.constants import Category, Constants
from libraries.context.context import Context
from libraries.logging.logging_helper import LoggingHelper
from libraries.ui.ui_helper import UIHelper

# pylint: disable=attribute-defined-outside-init, too-many-locals
# pylint: disable=too-many-instance-attributes


class ExecuteDialog:
    """Dialog to execute in the application"""

    def __init__(
        self,
        parent,
        callback: any
    ):
        """Initialize dialog"""

        self.__callback = callback

        # Create dialog
        self.dialog = tk.Toplevel(parent)

        # Fix dialog's title
        self.dialog.title(Context.get_text('execution'))

        # Fix dialog's size and position
        UIHelper.center_dialog(
            dialog=self.dialog,
            width=800,
            height=600
        )

        # Add a progress bar
        progress_bar = ttk.Progressbar(
            self.dialog,
            orient=tk.HORIZONTAL,
            length=500,
            mode='determinate'
        )
        progress_bar.pack(
            side=tk.TOP
        )

        self.progress_label = tk.Label(
            self.dialog
        )
        self.progress_label.pack(
            side=tk.TOP
        )

        # Create a textare with a scrollbar
        execution_frame = tk.Frame(self.dialog)
        execution_frame.pack(
            side=tk.TOP,
            fill=tk.BOTH,
            expand=True,
            padx=Constants.UI_PAD_BIG,
            pady=Constants.UI_PAD_BIG
        )

        execution_area = tk.Text(
            execution_frame,
            wrap=tk.WORD,
            width=50,
            height=10
        )
        execution_area.config(state=tk.DISABLED)
        execution_area.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        scrollbar = tk.Scrollbar(
            execution_frame,
            command=execution_area.yview
        )
        scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )
        execution_area.config(
            yscrollcommand=scrollbar.set
        )

        # Button to close
        button_close = tk.Button(
            self.dialog,
            command=self.__on_close
        )
        button_close.pack(
            side=tk.TOP,
            pady=Constants.UI_PAD_BIG
        )

        # Set log ui
        LoggingHelper.set_log_ui(
            log_ui=execution_area
        )

        # Initialize executor
        match(Context.get_selected_category()):
            case Category.TABLES:
                self.__executor = TablesExecutor(
                    progress_bar=progress_bar,
                    progress_label=self.progress_label,
                    button_close=button_close
                )

            case Category.PLAYLISTS:
                self.__executor = PlaylistsExecutor(
                    progress_bar=progress_bar,
                    progress_label=self.progress_label,
                    button_close=button_close
                )

            case Category.BDD_TABLES:
                self.__executor = BDDTablesExecutor(
                    progress_bar=progress_bar,
                    progress_label=self.progress_label,
                    button_close=button_close
                )

            case Category.CONFIGS:
                self.__executor = ConfigsExecutor(
                    progress_bar=progress_bar,
                    progress_label=self.progress_label,
                    button_close=button_close
                )

        # Execute in a thread
        self.execution_thread = threading.Thread(
            target=self.__executor.execute
        )
        self.execution_thread.start()

        # Bind closing event
        self.dialog.protocol("WM_DELETE_WINDOW", self.__on_close)

    def __close_after_execution_stopped(self):
        """Close after execution stopped"""

        # Update progress label
        self.progress_label.config(
            text=Context.get_text('waiting_for_stopping')
        )

        # Log a waiting message
        LoggingHelper.log_info(
            message=Context.get_text('waiting_for_stopping')
        )

        # Signal the thread to stop
        self.__executor.stop_execution()

        # Wait for the thread to finish
        self.execution_thread.join()

        # Unset log ui
        LoggingHelper.set_log_ui(
            log_ui=None
        )

        # Call back
        self.__callback(
            only_ids=self.__executor.get_ids_done()
        )

        # Close the dialog
        UIHelper.close_dialog(self.dialog)

    def __on_close(self):
        """Called when closing"""

        if self.__executor.is_execution_finished():
            # Unset log ui
            LoggingHelper.set_log_ui(
                log_ui=None
            )

            # Close the dialog
            UIHelper.close_dialog(self.dialog)

            # Call back
            self.__callback(
                only_ids=self.__executor.get_ids_done()
            )

        elif messagebox.askokcancel(
            Context.get_text('confirmation'),
            Context.get_text('confirm_stop_execution'),
            parent=self.dialog
        ):
            # Call a thread to close after execution stopped
            close_thread = threading.Thread(
                target=self.__close_after_execution_stopped
            )
            close_thread.start()
