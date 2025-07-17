#!/usr/bin/python3
"""Dialog to edit configs registry"""

import os
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog

from dialogs.waiting.waiting_dialog import WaitingDialog
from libraries.constants.constants import Component, Constants
from libraries.context.context import Context
from libraries.file.file_helper import FileHelper
from libraries.ui.ui_helper import UIHelper
from libraries.ui.ui_table import UITable
from libraries.verifier.verifier import Verifier

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-nested-blocks
# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument


class ConfigsRegistryEditorDialog:
    """Dialog to edit configs registry"""

    def __init__(
        self,
        parent,
        callback
    ):
        """Initialize dialog"""

        self.__callback = callback
        self.__table = None
        self.__current_item_id = None

        # Create dialog
        self.__dialog = tk.Toplevel(parent)

        # Fix dialog's title
        self.__dialog.title(Context.get_text('edit_configs'))

        # Fix dialog's size and position
        UIHelper.center_dialog(
            dialog=self.__dialog,
            width=800,
            height=450
        )

        # Force bg to avoid black panel when loading
        self.__dialog.configure(bg="SystemButtonFace")

        # Create top frame
        self.__top_frame = tk.Frame(
            self.__dialog
        )
        self.__top_frame.pack(
            side=tk.TOP,
            fill=tk.BOTH,
            expand=True
        )

        # Create bottom frame
        self.__bottom_frame = tk.Frame(
            self.__dialog
        )
        self.__bottom_frame.pack(
            side=tk.BOTTOM,
            fill=tk.BOTH,
            pady=Constants.UI_PAD_SMALL
        )

        # Create components
        self.__create_configs_components()
        self.__create_info_components()
        self.__create_close_components()

        # Bind closing event to stop all media
        self.__dialog.protocol("WM_DELETE_WINDOW", self.__on_close)

        # Select the first row
        self.__table.set_selected_rows([0])

    def __create_configs_components(self):
        """Create configs components"""

        # Create configs frames
        configs_label_frame = tk.LabelFrame(
            self.__top_frame,
            text=Context.get_text(Context.get_selected_category().value)
        )
        configs_label_frame.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=Constants.UI_PAD_BIG,
            pady=Constants.UI_PAD_BIG
        )
        configs_actions_frame = tk.Frame(configs_label_frame)
        configs_actions_frame.pack(
            side=tk.TOP,
            fill=tk.Y
        )
        configs_frame = tk.Frame(configs_label_frame)
        configs_frame.pack(
            side=tk.TOP,
            fill=tk.BOTH,
            expand=True,
            pady=Constants.UI_PAD_SMALL
        )

        # Create buttons to manage configs
        button_create_config = tk.Button(
            configs_actions_frame,
            text=Context.get_text(
                'target_action_create',
                target=Context.get_text('target_new_config')
            ),
            command=self.__create_config
        )
        button_create_config.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        button_delete_config = tk.Button(
            configs_actions_frame,
            text=Context.get_text(
                'target_action_delete',
                target=Context.get_text('target_config')
            ),
            command=self.__delete_config
        )
        button_delete_config.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )

        # Build rows
        selected_rows = Context.get_selected_configs_rows()

        rows = []
        for selected_row in selected_rows:
            row = {
                Constants.UI_TABLE_KEY_COL_SELECTION: False,
                Constants.UI_TABLE_KEY_COL_ID: selected_row[Constants.UI_TABLE_KEY_COL_ID],
                Constants.UI_TABLE_KEY_COL_NAME: selected_row[Constants.UI_TABLE_KEY_COL_NAME]
            }

            # Retrieve color
            row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                row=row
            )

            rows.append(row)

        # Create table
        self.__table = UITable(
            parent=configs_frame,
            on_selected_rows_change=self.__on_selected_rows_changed,
            rows=rows,
            multiple_selection=False
        )

    def __create_info_components(self):
        """Create info components"""

        # Create info frames
        info_label_frame = tk.LabelFrame(
            self.__top_frame,
            text=Context.get_text('info_title')
        )
        info_label_frame.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            padx=Constants.UI_PAD_BIG,
            pady=Constants.UI_PAD_BIG
        )
        info_frame = tk.Frame(info_label_frame)
        info_frame.pack(
            side=tk.TOP,
            fill=tk.BOTH
        )
        info_bottom_actions_frame = tk.Frame(info_label_frame)
        info_bottom_actions_frame.pack(
            side=tk.BOTTOM,
            pady=Constants.UI_PAD_SMALL,
            fill=tk.Y
        )

    def __create_close_components(self):
        """Create close components"""

        # Create button to close
        button_close = tk.Button(
            self.__bottom_frame,
            text=Context.get_text('close'),
            command=self.__on_close
        )
        button_close.pack(
            side=tk.TOP
        )

    def __run_create_config(self, should_interrupt):
        """Run create a new config"""

        # Create the config path
        os.makedirs(os.path.join(
            Context.get_configs_path(),
            self.new_config,
            Component.REGISTRY.name.lower()
        ))

        # Change rows
        rows = self.__table.list_rows()
        row = {
            Constants.UI_TABLE_KEY_COL_SELECTION: False,
            Constants.UI_TABLE_KEY_COL_ID: self.new_config,
            Constants.UI_TABLE_KEY_COL_NAME: self.new_config
        }
        row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
            row=row
        )
        rows.insert(0, row)
        self.__table.set_rows(
            rows=rows
        )

        # Select the first config
        self.__table.set_selected_rows(
            rows_idx=[0]
        )

    def __create_config(self):
        """Create a new config"""

        # Ask an entry for the new config
        self.new_config = simpledialog.askstring(
            Context.get_text('confirmation'),
            Context.get_text(
                'confirm_create_config'
            ),
            parent=self.__dialog
        )

        if self.new_config is None:
            return

        # Check if config already exists
        if FileHelper.is_folder_exists(
            folder_path=self.new_config
        ):
            messagebox.showerror(
                title=Context.get_text('error_title'),
                message=Context.get_text(
                    'error_config_already_exists',
                    config=self.new_config
                ),
                parent=self.__dialog
            )
            return

        # Execute the process in a waiting dialog
        WaitingDialog(
            parent=self.__dialog,
            process_name=Context.get_text('process_creation'),
            process_function=self.__run_create_config
        )

    def __run_delete_config(self, should_interrupt):
        """Run delete a config"""

        # Delete the folder
        FileHelper.delete_folder(
            folder_path=os.path.join(
                Context.get_configs_path(),
                self.__current_item_id
            )
        )

        # Change rows
        rows = self.__table.list_rows()

        if len(rows) == 1:
            self.__on_close()
            return

        for row in rows:

            if should_interrupt():
                return

            if row[Constants.UI_TABLE_KEY_COL_ID] == self.__current_item_id:
                rows.remove(row)
        self.__table.set_rows(
            rows=rows
        )

        # Select the first table
        self.__table.set_selected_rows(
            rows_idx=[0]
        )

    def __delete_config(self):
        """Delete a config"""

        # Ask a confirmation to delete
        if not messagebox.askokcancel(
            Context.get_text('confirmation'),
            Context.get_text(
                'confirm_delete_config',
                config=self.__current_item_id
            ),
            parent=self.__dialog
        ):
            return

        # Execute the process in a waiting dialog
        WaitingDialog(
            parent=self.__dialog,
            process_name=Context.get_text('process_deletion'),
            process_function=self.__run_delete_config
        )

    def __on_selected_rows_changed(self):
        """Called when selected rows changed"""

        # Retrieve selected rows
        selected_rows = self.__table.get_selected_rows()

        # Do nothing if no selected row
        if len(selected_rows) != 1:
            return

        # Store selected current item's id
        self.__current_item_id = selected_rows[0][Constants.UI_TABLE_KEY_COL_ID]

    def __on_close(self):
        """Called when closing"""

        # Call back
        self.__callback()

        # Close the dialog
        UIHelper.close_dialog(self.__dialog)
