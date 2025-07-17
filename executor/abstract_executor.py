#!/usr/bin/python3
"""Abstract Executor"""

from abc import ABC, abstractmethod
from datetime import datetime
import os
import threading
import tkinter as tk
from tkinter import ttk

from libraries.constants.constants import Action, Category, Constants
from libraries.context.context import Context
from libraries.logging.logging_helper import LoggingHelper


class AbstractExecutor(ABC):
    """Abstract Executor (Common for all executors)"""

    def __init__(
        self,
        progress_bar: ttk.Progressbar,
        progress_label: tk.Label,
        button_close: tk.Button
    ):
        """Initialize executor"""

        self.__execution_finished: bool = False
        self.__stop_execution = threading.Event()
        self.__progress_bar = progress_bar
        self.__progress_label = progress_label
        self.__button_close = button_close
        self.__copy_folder_path = None
        if Context.get_selected_action() == Action.COPY:
            self.__copy_folder_path = os.path.join(
                Context.get_selected_folder_path(),
                f'copy_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            )

    def stop_execution(self):
        """Stop execution"""

        self.__stop_execution.set()

    def is_execution_finished(self) -> bool:
        """Specify if execution finished"""

        return self.__execution_finished

    def get_copy_folder_path(self) -> str:
        """Get copy folder's path"""

        return self.__copy_folder_path

    def execute(self):
        """Execute"""

        # Fix text Stop for button to close
        self.__button_close.config(
            text=Context.get_text('stop')
        )

        # Show message for execution started
        LoggingHelper.log_info(
            message=Context.get_text(
                'execution_started',
                category=Context.get_text(
                    Context.get_selected_category().value
                ),
                action=Context.get_text(
                    Context.get_selected_action().value,
                    category=Context.get_text(
                        Context.get_selected_category().value
                    )
                )
            )
        )

        # Do execution depending on selected category
        rows = []
        match(Context.get_selected_category()):
            case Category.TABLES:
                rows = Context.get_selected_tables_rows()

            case Category.PLAYLISTS:
                rows = Context.get_selected_playlists_rows()

            case Category.CONFIGS_FILES:
                rows = Context.get_selected_configs_rows()

        # Initialize progress bar
        self.__progress_bar.config(maximum=len(rows))

        item_current_counter = 1
        for row in rows:

            # Continue if execution stopped
            if self.__stop_execution.is_set():
                return

            # Increment progress bar
            self.__progress_bar['value'] = item_current_counter
            self.__progress_label.config(
                text=Context.get_text(
                    'execution_in_progress',
                    item_name=row[Constants.UI_TABLE_KEY_COL_NAME],
                    item_current_counter=item_current_counter,
                    item_total_counter=len(rows)
                )
            )

            # Show execution line for the current item
            LoggingHelper.log_info(
                message=Context.get_text(
                    'execution_in_progress',
                    item_name=row[Constants.UI_TABLE_KEY_COL_NAME],
                    item_current_counter=item_current_counter,
                    item_total_counter=len(rows)
                )
            )

            # Do execution for the current item
            try:
                self.do_execution(
                    item_id=row[Constants.UI_TABLE_KEY_COL_ID]
                )
            except Exception as exc:
                LoggingHelper.log_error(
                    Context.get_text(
                        'error_execution',
                        item_name=row[Constants.UI_TABLE_KEY_COL_NAME],
                        error=str(exc)
                    ),
                    exc
                )

                # Stop execution if error
                self.__execution_finished = True
                return

            item_current_counter += 1

        # Finish progression
        self.__progress_bar['value'] = item_current_counter
        self.__progress_label.config(
            text=Context.get_text('execution_finished')
        )

        # Show message for execution finished
        LoggingHelper.log_info(
            message=Context.get_text('execution_finished')
        )
        self.__execution_finished = True

        # Fix text Close for button to close
        self.__button_close.config(
            text=Context.get_text('close')
        )

    @abstractmethod
    def do_execution(self, item_id: str):
        """Do execution for an item"""
