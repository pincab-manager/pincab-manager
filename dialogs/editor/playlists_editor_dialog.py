#!/usr/bin/python3
"""Dialog to edit playlists"""

import os
import re
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog

from dialogs.waiting.waiting_dialog import WaitingDialog
from libraries.bdd.bdd_helper import BddHelper
from libraries.constants.constants import Constants
from libraries.context.context import Context
from libraries.csv.csv_helper import CsvHelper
from libraries.file.file_helper import FileHelper
from libraries.list.list_helper import ListHelper
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


class PlaylistsEditorDialog:
    """Dialog to edit playlists"""

    def __init__(
        self,
        parent,
        callback
    ):
        """Initialize dialog"""

        self.__callback = callback
        self.__table = None
        self.__current_item_id = None
        self.__current_csv_item = None

        # Create dialog
        self.__dialog = tk.Toplevel(parent)

        # Fix dialog's title
        self.__dialog.title(Context.get_text('edit_playlists'))

        # Fix dialog's size and position
        UIHelper.center_dialog(
            dialog=self.__dialog,
            width=1000,
            height=900
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
        self.__create_playlists_components()
        self.__create_info_components()
        self.__create_close_components()

        # Bind closing event
        self.__dialog.protocol("WM_DELETE_WINDOW", self.__on_close)

        # Select the first row
        self.__table.set_selected_rows([0])

    def __create_playlists_components(self):
        """Create playlists components"""

        # Create playlists frames
        playlists_label_frame = tk.LabelFrame(
            self.__top_frame,
            text=Context.get_text(Context.get_selected_category().value)
        )
        playlists_label_frame.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=Constants.UI_PAD_BIG,
            pady=Constants.UI_PAD_BIG
        )
        playlists_actions_frame = tk.Frame(playlists_label_frame)
        playlists_actions_frame.pack(
            side=tk.TOP,
            fill=tk.Y
        )
        playlists_frame = tk.Frame(playlists_label_frame)
        playlists_frame.pack(
            side=tk.TOP,
            fill=tk.BOTH,
            expand=True,
            pady=Constants.UI_PAD_SMALL
        )

        # Create buttons to manage playlists
        button_create_playlist = tk.Button(
            playlists_actions_frame,
            text=Context.get_text(
                'target_action_create',
                target=Context.get_text('target_new_playlist')
            ),
            command=self.__create_playlist
        )
        button_create_playlist.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        button_delete_playlist = tk.Button(
            playlists_actions_frame,
            text=Context.get_text(
                'target_action_delete',
                target=Context.get_text('target_playlist')
            ),
            command=self.__delete_playlist
        )
        button_delete_playlist.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )

        # Build rows
        selected_rows = Context.get_selected_playlists_rows()

        rows = []
        for selected_row in selected_rows:
            row = {
                Constants.UI_TABLE_KEY_COL_SELECTION: False,
                Constants.UI_TABLE_KEY_COL_ID: selected_row[Constants.UI_TABLE_KEY_COL_ID],
                Constants.UI_TABLE_KEY_COL_NAME: selected_row[Constants.UI_TABLE_KEY_COL_NAME],
                Constants.UI_TABLE_KEY_COL_UNIQUE_VERSION: selected_row[
                    Constants.UI_TABLE_KEY_COL_UNIQUE_VERSION]
            }

            # Retrieve color
            row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                row=row
            )

            rows.append(row)

        # Create table
        self.__table = UITable(
            parent=playlists_frame,
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
        info_top_actions_frame = tk.Frame(info_label_frame)
        info_top_actions_frame.pack(
            side=tk.TOP,
            fill=tk.Y
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

        # Create buttons to manage versions
        self.button_explore_version = tk.Button(
            info_top_actions_frame,
            text=Context.get_text(
                'target_action_explore',
                target=Context.get_text('target_version')
            ),
            command=self.__explore_version
        )
        self.button_explore_version.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )

        self.button_rename_version = tk.Button(
            info_top_actions_frame,
            text=Context.get_text(
                'target_action_rename',
                target=Context.get_text('target_version')
            ),
            command=self.__rename_version
        )
        self.button_rename_version.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )

        self.button_create_version = tk.Button(
            info_top_actions_frame,
            text=Context.get_text(
                'target_action_create',
                target=Context.get_text('target_new_version')
            ),
            command=self.__create_version
        )
        self.button_create_version.config(state=tk.DISABLED)
        self.button_create_version.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )

        self.button_delete_version = tk.Button(
            info_top_actions_frame,
            text=Context.get_text(
                'target_action_delete',
                target=Context.get_text('target_version')
            ),
            command=self.__delete_version
        )
        self.button_delete_version.config(state=tk.DISABLED)
        self.button_delete_version.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )

        # Create components for current version
        info_current_version_frame = tk.Frame(info_frame)
        info_current_version_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            pady=Constants.UI_PAD_SMALL
        )
        info_current_version_label = tk.Label(
            info_current_version_frame,
            text=Context.get_text('info_current_version')
        )
        info_current_version_label.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.info_current_version_combo = ttk.Combobox(
            info_current_version_frame
        )
        self.info_current_version_combo.config(state="readonly")
        self.info_current_version_combo.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.info_current_version_combo.bind(
            "<<ComboboxSelected>>",
            self.__on_entry_changed
        )

        # Create components for available
        info_available_frame = tk.Frame(info_frame)
        info_available_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            pady=Constants.UI_PAD_SMALL
        )
        self.info_available_checkbox_var = tk.BooleanVar()
        self.info_available_checkbox_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.info_available_checkbox = tk.Checkbutton(
            info_available_frame,
            variable=self.info_available_checkbox_var
        )
        self.info_available_checkbox.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        info_available_label = tk.Label(
            info_available_frame,
            text=Context.get_text('info_available')
        )
        info_available_label.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        info_available_label.bind(
            "<Button-1>",
            lambda e: self.info_available_checkbox.invoke()
        )

        # Create components for id
        info_id_frame = tk.Frame(info_frame)
        info_id_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            pady=Constants.UI_PAD_SMALL
        )
        info_id_label = tk.Label(
            info_id_frame,
            text=Context.get_text('info_id')
        )
        info_id_label.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.info_id_entry_var = tk.StringVar()
        self.info_id_entry_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.info_id_entry = tk.Entry(
            info_id_frame,
            textvariable=self.info_id_entry_var,
            width=40
        )
        self.info_id_entry.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )

        # Create components for name
        info_name_frame = tk.Frame(info_frame)
        info_name_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            pady=Constants.UI_PAD_SMALL
        )
        info_name_label = tk.Label(
            info_name_frame,
            text=Context.get_text('info_name')
        )
        info_name_label.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.info_name_entry_var = tk.StringVar()
        self.info_name_entry_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.info_name_entry = tk.Entry(
            info_name_frame,
            textvariable=self.info_name_entry_var,
            width=40
        )
        self.info_name_entry.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )

        # Create components for sql
        info_sql_frame = tk.Frame(info_frame)
        info_sql_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            pady=Constants.UI_PAD_SMALL
        )
        info_sql_label = tk.Label(
            info_sql_frame,
            text=Context.get_text('info_sql')
        )
        info_sql_label.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.info_sql_entry_var = tk.StringVar()
        self.info_sql_entry_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.info_sql_entry = tk.Entry(
            info_sql_frame,
            textvariable=self.info_sql_entry_var,
            width=40
        )
        self.info_sql_entry.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )

        # Create buttons to cancel and validate
        self.button_cancel = tk.Button(
            info_bottom_actions_frame,
            text=Context.get_text(
                'target_action_cancel',
                target=Context.get_text('target_entries')
            ),
            command=self.__init_info_entries
        )
        self.button_cancel.config(state=tk.DISABLED)
        self.button_cancel.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )

        self.button_validate = tk.Button(
            info_bottom_actions_frame,
            text=Context.get_text(
                'target_action_validate',
                target=Context.get_text('target_entries')
            ),
            command=self.__validate
        )
        self.button_validate.config(state=tk.DISABLED)
        self.button_validate.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
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

    def __on_entry_changed(self, *_):
        """Called when an entry changed"""

        self.button_cancel.config(state=tk.NORMAL)
        self.button_validate.config(state=tk.NORMAL)

        if self.__current_csv_item[Constants.CSV_COL_VERSION] != \
                self.info_current_version_combo.get():
            self.button_delete_version.config(state=tk.NORMAL)
        else:
            self.button_delete_version.config(state=tk.DISABLED)

    def __run_validate(self, should_interrupt):
        """Run validate"""

        # Modify the playlist in the CSV
        csv_items = CsvHelper.read_data(
            file_path=Context.get_csv_path()
        )

        for csv_item in csv_items:
            if csv_item[Constants.CSV_COL_ID] != self.__current_csv_item[Constants.CSV_COL_ID]:
                continue

            if should_interrupt():
                return

            # Check if current version changed
            if csv_item[Constants.CSV_COL_VERSION] != self.info_current_version_combo.get():
                csv_item[Constants.CSV_COL_VERSION] = self.info_current_version_combo.get()

            # Check if name changed
            if BddHelper.is_not_null_value(self.info_name_entry_var.get()) and \
                    csv_item[Constants.CSV_COL_NAME] != self.info_name_entry_var.get():
                csv_item[Constants.CSV_COL_NAME] = self.info_name_entry_var.get()

            # Check if id changed
            if BddHelper.is_not_null_value(self.info_id_entry_var.get()) and \
                    csv_item[Constants.CSV_COL_ID] != self.info_id_entry_var.get():

                # Retrieve new playlist folder
                new_playlist_folder = os.path.join(
                    Context.get_working_path(),
                    'playlists',
                    self.info_id_entry_var.get()
                )

                # Move the folder
                FileHelper.move_folder(
                    source_folder_path=os.path.join(
                        Context.get_working_path(),
                        'playlists',
                        csv_item[Constants.CSV_COL_ID]
                    ),
                    destination_folder_path=new_playlist_folder
                )

                # Rename all files
                for relative_path in FileHelper.list_relative_paths(
                    folder_path=new_playlist_folder,
                    file_name=f'{csv_item[Constants.CSV_COL_ID]}*'
                ):
                    if csv_item[Constants.CSV_COL_ID] not in relative_path:
                        continue

                    # Move the file
                    FileHelper.move_file(
                        source_file_path=os.path.join(
                            new_playlist_folder,
                            relative_path
                        ),
                        destination_file_path=os.path.join(
                            new_playlist_folder,
                            relative_path.replace(
                                csv_item[Constants.CSV_COL_ID],
                                self.info_id_entry_var.get()
                            )
                        )
                    )

                csv_item[Constants.CSV_COL_ID] = self.info_id_entry_var.get()

            # Check if sql changed
            if csv_item[Constants.CSV_COL_SQL] != self.info_sql_entry_var.get():
                if BddHelper.is_not_null_value(self.info_sql_entry_var.get()):
                    csv_item[Constants.CSV_COL_SQL] = self.info_sql_entry_var.get()
                else:
                    csv_item[Constants.CSV_COL_SQL] = None

            # Check if available changed
            if csv_item[Constants.CSV_COL_AVAILABLE] != self.info_available_checkbox_var.get():
                if self.info_available_checkbox_var.get():
                    csv_item[Constants.CSV_COL_AVAILABLE] = Constants.CSV_YES_VALUE
                else:
                    csv_item[Constants.CSV_COL_AVAILABLE] = Constants.CSV_NO_VALUE

            self.__current_csv_item = csv_item

        CsvHelper.write_data(
            file_path=Context.get_csv_path(),
            data=csv_items
        )

        # Change rows
        row_idx = 0
        selected_rows = self.__table.get_selected_rows()
        rows = self.__table.list_rows()
        for row in rows:

            if should_interrupt():
                return

            if row in selected_rows:
                row[Constants.UI_TABLE_KEY_COL_ID] = self.__current_csv_item[
                    Constants.CSV_COL_ID]
                row[Constants.UI_TABLE_KEY_COL_NAME] = self.__current_csv_item[
                    Constants.CSV_COL_NAME]
                break
            row_idx += 1

        self.__table.set_rows(
            rows=rows
        )

        # Select the playlist
        self.__table.set_selected_rows(
            rows_idx=[row_idx]
        )

        # Reinitialize info entries
        self.__init_info_entries()

    def __validate(self):
        """Validate"""

        # Execute the process in a waiting dialog
        WaitingDialog(
            parent=self.__dialog,
            process_name=Context.get_text('process_execution'),
            process_function=self.__run_validate
        )

    def __run_create_playlist(self, should_interrupt):
        """Run create a new playlist"""

        # Create the media path
        os.makedirs(os.path.join(
            self.playlist_folder,
            self.new_playlist_version,
            'media'
        ))

        # Add the playlist in the CSV
        csv_items = CsvHelper.read_data(
            file_path=Context.get_csv_path()
        )

        csv_items.append({
            Constants.CSV_COL_AVAILABLE: Constants.CSV_YES_VALUE,
            Constants.CSV_COL_VERSION: self.new_playlist_version,
            Constants.CSV_COL_NAME: self.new_playlist_name,
            Constants.CSV_COL_ID: self.new_playlist_id,
            Constants.CSV_COL_SQL: None
        })

        CsvHelper.write_data(
            file_path=Context.get_csv_path(),
            data=csv_items
        )

        # Change rows
        rows = self.__table.list_rows()
        row = {
            Constants.UI_TABLE_KEY_COL_SELECTION: False,
            Constants.UI_TABLE_KEY_COL_ID: self.new_playlist_id,
            Constants.UI_TABLE_KEY_COL_NAME: self.new_playlist_name,
            Constants.UI_TABLE_KEY_COL_UNIQUE_VERSION: True
        }
        row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
            row=row
        )
        rows.insert(0, row)
        self.__table.set_rows(
            rows=rows
        )

        # Select the first playlist
        self.__table.set_selected_rows(
            rows_idx=[0]
        )

    def __create_playlist(self):
        """Create a new playlist"""

        # Ask an entry for the new playlist's id
        self.new_playlist_id = simpledialog.askstring(
            Context.get_text('confirmation'),
            Context.get_text(
                'confirm_create_playlist_1'
            ),
            parent=self.__dialog
        )

        if self.new_playlist_id is None:
            return

        # Retrieve the playlist's folder
        self.playlist_folder = os.path.join(
            Context.get_working_path(),
            'playlists',
            self.new_playlist_id
        )

        # Check if playlist already exists
        if FileHelper.is_folder_exists(
            folder_path=self.playlist_folder
        ):
            messagebox.showerror(
                title=Context.get_text('error_title'),
                message=Context.get_text(
                    'error_playlist_already_exists',
                    playlist=self.new_playlist_id
                ),
                parent=self.__dialog
            )
            return

        # Ask an entry for the new playlist's name
        self.new_playlist_name = simpledialog.askstring(
            Context.get_text('confirmation'),
            Context.get_text(
                'confirm_create_playlist_2'
            ),
            parent=self.__dialog
        )

        if self.new_playlist_name is None:
            return

        # First letter has to be an uppercase for the name
        self.new_playlist_name = self.new_playlist_name[0].upper(
        ) + self.new_playlist_name[1:]

        # Ask an entry for the new version
        while True:
            self.new_playlist_version = simpledialog.askstring(
                Context.get_text('confirmation'),
                Context.get_text(
                    'confirm_create_playlist_3'
                ),
                parent=self.__dialog
            )
            if self.new_playlist_version is None:
                break
            if re.fullmatch(r"[a-zA-Z0-9.]+", self.new_playlist_version):
                break

        if self.new_playlist_version is None:
            return

        # Execute the process in a waiting dialog
        WaitingDialog(
            parent=self.__dialog,
            process_name=Context.get_text('process_creation'),
            process_function=self.__run_create_playlist
        )

    def __run_delete_playlist(self, should_interrupt):
        """Run delete a playlist"""

        # Delete the folder
        FileHelper.delete_folder(
            folder_path=os.path.join(
                Context.get_working_path(),
                'playlists',
                self.__current_item_id
            )
        )

        # Remove the playlist from the CSV
        csv_items = CsvHelper.read_data(
            file_path=Context.get_csv_path()
        )

        csv_items.remove(self.__current_csv_item)

        CsvHelper.write_data(
            file_path=Context.get_csv_path(),
            data=csv_items
        )

        # Change rows
        rows = self.__table.list_rows()

        if len(rows) == 1:
            self.__on_close()
            return

        for row in rows:

            if should_interrupt():
                return

            if row[Constants.UI_TABLE_KEY_COL_ID] == self.__current_csv_item[Constants.CSV_COL_ID]:
                rows.remove(row)
        self.__table.set_rows(
            rows=rows
        )

        # Select the first playlist
        self.__table.set_selected_rows(
            rows_idx=[0]
        )

    def __delete_playlist(self):
        """Delete a playlist"""

        # Ask a confirmation to delete
        if not messagebox.askokcancel(
            Context.get_text('confirmation'),
            Context.get_text(
                'confirm_delete_playlist',
                playlist=self.__current_csv_item[Constants.CSV_COL_NAME]
            ),
            parent=self.__dialog
        ):
            return

        # Execute the process in a waiting dialog
        WaitingDialog(
            parent=self.__dialog,
            process_name=Context.get_text('process_deletion'),
            process_function=self.__run_delete_playlist
        )

    def __run_create_version(self, should_interrupt):
        """Run create a new version"""

        # Copy folder to the new version
        FileHelper.copy_folder(
            source_folder_path=os.path.join(
                Context.get_working_path(),
                'playlists',
                self.__current_item_id,
                self.info_current_version_combo.get()
            ),
            destination_folder_path=os.path.join(
                Context.get_working_path(),
                'playlists',
                self.__current_item_id,
                self.new_version
            )
        )

        # Add the new version and select it
        all_versions = list(self.info_current_version_combo["values"])
        all_versions.append(self.new_version)
        self.info_current_version_combo.config(
            values=all_versions
        )
        self.info_current_version_combo.set(self.new_version)
        self.button_delete_version.config(state=tk.NORMAL)

        # Change rows
        rows = self.__table.list_rows()
        row_idx = 0
        for row in rows:

            if should_interrupt():
                return

            if row[Constants.UI_TABLE_KEY_COL_ID] == self.__current_csv_item[Constants.CSV_COL_ID]:
                row[Constants.UI_TABLE_KEY_COL_UNIQUE_VERSION] = Verifier.verify_playlist_version(
                    csv_playlist_id=self.__current_csv_item[Constants.CSV_COL_ID]
                )
                row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                    row=row
                )
                break
            row_idx += 1
        self.__table.set_rows(
            rows=rows
        )
        self.__table.set_selected_rows(
            rows_idx=[row_idx]
        )

    def __create_version(self):
        """Create a new version"""

        all_versions = list(self.info_current_version_combo["values"])

        # Ask an entry for the new version
        while True:
            self.new_version = simpledialog.askstring(
                Context.get_text('confirmation'),
                Context.get_text(
                    'confirm_create_version',
                    version=self.info_current_version_combo.get()
                ),
                parent=self.__dialog
            )
            if self.new_version is None:
                break
            if self.new_version in all_versions:
                continue
            if re.fullmatch(r"[a-zA-Z0-9.]+", self.new_version):
                break

        if self.new_version is None:
            return

        # Execute the process in a waiting dialog
        WaitingDialog(
            parent=self.__dialog,
            process_name=Context.get_text('process_creation'),
            process_function=self.__run_create_version
        )

    def __run_rename_version(self, should_interrupt):
        """Run rename a version"""

        # Move folder to the new version
        FileHelper.move_folder(
            source_folder_path=os.path.join(
                Context.get_working_path(),
                'playlists',
                self.__current_item_id,
                self.info_current_version_combo.get()
            ),
            destination_folder_path=os.path.join(
                Context.get_working_path(),
                'playlists',
                self.__current_item_id,
                self.new_version
            )
        )

        # If the old version is the current version
        csv_items = CsvHelper.read_data(
            file_path=Context.get_csv_path()
        )
        for csv_item in csv_items:
            if csv_item[Constants.CSV_COL_ID] != self.__current_csv_item[Constants.CSV_COL_ID]:
                continue

            if should_interrupt():
                return

            # Check if current version changed
            if csv_item[Constants.CSV_COL_VERSION] == self.info_current_version_combo.get():
                csv_item[Constants.CSV_COL_VERSION] = self.new_version

                CsvHelper.write_data(
                    file_path=Context.get_csv_path(),
                    data=csv_items
                )

            break

        # Replace the old version by the new version and select it
        all_versions = list(self.info_current_version_combo["values"])
        all_versions.remove(self.info_current_version_combo.get())
        all_versions.append(self.new_version)
        self.info_current_version_combo.config(
            values=all_versions
        )
        self.info_current_version_combo.set(self.new_version)
        self.button_delete_version.config(state=tk.NORMAL)

        # Change rows
        rows = self.__table.list_rows()
        row_idx = 0
        for row in rows:
            if row[Constants.UI_TABLE_KEY_COL_ID] == self.__current_csv_item[Constants.CSV_COL_ID]:
                row[Constants.UI_TABLE_KEY_COL_UNIQUE_VERSION] = Verifier.verify_playlist_version(
                    csv_playlist_id=self.__current_csv_item[Constants.CSV_COL_ID]
                )
                row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                    row=row
                )
                break
            row_idx += 1
        self.__table.set_rows(
            rows=rows
        )
        self.__table.set_selected_rows(
            rows_idx=[row_idx]
        )

    def __rename_version(self):
        """Rename a version"""

        all_versions = list(self.info_current_version_combo["values"])

        # Ask an entry for the new version
        while True:
            self.new_version = simpledialog.askstring(
                Context.get_text('confirmation'),
                Context.get_text('confirm_rename'),
                parent=self.__dialog
            )
            if self.new_version is None:
                break
            if self.new_version in all_versions:
                continue
            if re.fullmatch(r"[a-zA-Z0-9.]+", self.new_version):
                break

        if self.new_version is None:
            return

        # Execute the process in a waiting dialog
        WaitingDialog(
            parent=self.__dialog,
            process_name=Context.get_text('process_renaming'),
            process_function=self.__run_rename_version
        )

    def __run_delete_version(self, should_interrupt):
        """Run delete a version"""

        # Delete the folder
        FileHelper.delete_folder(
            folder_path=os.path.join(
                Context.get_working_path(),
                'playlists',
                self.__current_item_id,
                self.info_current_version_combo.get()
            )
        )

        # Remove the deleted version and select the current selected version
        all_versions = list(self.info_current_version_combo["values"])
        all_versions.remove(self.info_current_version_combo.get())
        self.info_current_version_combo.config(
            values=all_versions
        )
        self.info_current_version_combo.set(
            self.__current_csv_item[Constants.CSV_COL_VERSION]
        )
        self.button_delete_version.config(state=tk.DISABLED)

        # Change rows
        rows = self.__table.list_rows()
        row_idx = 0
        for row in rows:

            if should_interrupt():
                return

            if row[Constants.UI_TABLE_KEY_COL_ID] == self.__current_csv_item[Constants.CSV_COL_ID]:
                row[Constants.UI_TABLE_KEY_COL_UNIQUE_VERSION] = Verifier.verify_playlist_version(
                    csv_playlist_id=self.__current_csv_item[Constants.CSV_COL_ID]
                )
                row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                    row=row
                )
                break
            row_idx += 1
        self.__table.set_rows(
            rows=rows
        )
        self.__table.set_selected_rows(
            rows_idx=[row_idx]
        )

    def __delete_version(self):
        """Delete a version"""

        # Ask a confirmation to delete
        if not messagebox.askokcancel(
            Context.get_text('confirmation'),
            Context.get_text(
                'confirm_delete_version',
                version=self.info_current_version_combo.get()
            ),
            parent=self.__dialog
        ):
            return

        # Execute the process in a waiting dialog
        WaitingDialog(
            parent=self.__dialog,
            process_name=Context.get_text('process_deletion'),
            process_function=self.__run_delete_version
        )

    def __explore_version(self):
        """Explore the folder for the selected version"""

        FileHelper.explore_folder(
            folder_path=os.path.join(
                Context.get_working_path(),
                'playlists',
                self.__current_item_id,
                self.info_current_version_combo.get()
            )
        )

    def __init_info_entries(self):
        """Initialize info entries"""

        # Retrieve item's version
        item_version = self.__current_csv_item.get(
            Constants.CSV_COL_VERSION,
            Constants.LATEST_PATH
        )

        # Retrieve all versions and current version
        all_versions = FileHelper.list_sub_directories(
            folder_path=os.path.join(
                Context.get_working_path(),
                'playlists',
                self.__current_item_id
            )
        )

        # Update versions components
        self.info_current_version_combo.config(
            values=all_versions
        )
        self.info_current_version_combo.set(item_version)
        self.button_delete_version.config(state=tk.DISABLED)
        self.button_create_version.config(state=tk.NORMAL)

        # Update entries components
        self.info_id_entry_var.set(
            self.__current_csv_item[Constants.CSV_COL_ID]
        )

        self.info_name_entry_var.set(
            self.__current_csv_item[Constants.CSV_COL_NAME]
        )

        if BddHelper.is_not_null_value(self.__current_csv_item[Constants.CSV_COL_SQL]):
            self.info_sql_entry_var.set(
                self.__current_csv_item[Constants.CSV_COL_SQL]
            )
        else:
            self.info_sql_entry_var.set('')

        if self.__current_csv_item[Constants.CSV_COL_AVAILABLE] == Constants.CSV_YES_VALUE:
            self.info_available_checkbox_var.set(True)
        else:
            self.info_available_checkbox_var.set(False)

        self.button_cancel.config(state=tk.DISABLED)
        self.button_validate.config(state=tk.DISABLED)

        # Focus on table
        self.__table.focus()

    def __on_selected_rows_changed(self):
        """Called when selected rows changed"""

        # Retrieve selected rows
        selected_rows = self.__table.get_selected_rows()

        # Do nothing if no selected row
        if len(selected_rows) != 1:
            return

        # Store selected current item's id
        self.__current_item_id = selected_rows[0][Constants.UI_TABLE_KEY_COL_ID]
        self.__current_csv_item = ListHelper.select_item(
            item_id=self.__current_item_id,
            a_list=CsvHelper.read_data(
                file_path=Context.get_csv_path()
            ),
            id_column=Constants.CSV_COL_ID
        )

        # Initialize info entries
        self.__init_info_entries()

    def __on_close(self):
        """Called when closing"""

        # Call back
        self.__callback()

        # Close the dialog
        UIHelper.close_dialog(self.__dialog)
