#!/usr/bin/python3
"""Dialog to edit tables"""

import os
import re
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog

import vlc

from dialogs.waiting.waiting_dialog import WaitingDialog
from libraries.bdd.bdd_helper import BddHelper
from libraries.cmd.cmd_helper import CmdHelper
from libraries.constants.constants import Component, Constants, Emulator
from libraries.context.context import Context
from libraries.csv.csv_helper import CsvHelper
from libraries.file.file_helper import FileHelper
from libraries.list.list_helper import ListHelper
from libraries.ui.ui_helper import UIHelper
from libraries.ui.ui_table import UITable
from libraries.verifier.verifier import Verifier
from libraries.weblink.weblink_helper import WeblinkHelper

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


class TablesEditorDialog:
    """Dialog to edit tables"""

    def __init__(
        self,
        parent,
        callback
    ):
        """Initialize dialog"""

        self.__callback = callback
        self.__modified_ids = []
        self.__table = None
        self.__vlc_window = None
        self.__vlc_media_player = None
        self.__current_item_id = None
        self.__current_csv_item = None
        self.__current_folder_path = None
        self.__current_version_path = None
        self.__current_videos_path = None
        self.__context_menu_commands_count = 0

        # Initialize VLC
        self.__vlc_instance = vlc.Instance()

        # Create dialog
        self.__dialog = tk.Toplevel(parent)

        # Fix dialog's title
        self.__dialog.title(Context.get_text('edit_tables'))

        # Fix dialog's size and position
        UIHelper.center_dialog(
            dialog=self.__dialog,
            width=1200,
            height=1000
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
        self.__create_tables_components()
        self.__create_info_components()
        self.__create_close_components()

        # Bind closing event
        self.__dialog.protocol("WM_DELETE_WINDOW", self.__on_close)

        # Select the first row
        self.__table.set_selected_rows([0])

        # Advise that selected version changed
        self.__on_selected_version_changed()

    def __create_tables_components(self):
        """Create tables components"""

        # Create tables frames
        tables_label_frame = tk.LabelFrame(
            self.__top_frame,
            text=Context.get_text(Context.get_selected_category().value)
        )
        tables_label_frame.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=Constants.UI_PAD_BIG,
            pady=Constants.UI_PAD_BIG
        )
        tables_actions_frame = tk.Frame(tables_label_frame)
        tables_actions_frame.pack(
            side=tk.TOP,
            fill=tk.Y
        )
        tables_frame = tk.Frame(tables_label_frame)
        tables_frame.pack(
            side=tk.TOP,
            fill=tk.BOTH,
            expand=True,
            pady=Constants.UI_PAD_SMALL
        )

        # Create buttons to manage tables
        button_create_table = tk.Button(
            tables_actions_frame,
            text=Context.get_text(
                'target_action_create',
                target=Context.get_text('target_new_table')
            ),
            command=self.__create_table
        )
        button_create_table.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        button_delete_table = tk.Button(
            tables_actions_frame,
            text=Context.get_text(
                'target_action_delete',
                target=Context.get_text('target_table')
            ),
            command=self.__delete_table
        )
        button_delete_table.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )

        # Build rows
        selected_rows = Context.get_selected_tables_rows()

        rows = []
        for selected_row in selected_rows:
            row = {
                Constants.UI_TABLE_KEY_COL_SELECTION: False,
                Constants.UI_TABLE_KEY_COL_ID: selected_row[Constants.UI_TABLE_KEY_COL_ID],
                Constants.UI_TABLE_KEY_COL_NAME: selected_row[Constants.UI_TABLE_KEY_COL_NAME],
                Constants.UI_TABLE_KEY_COL_LATEST_VERSION: selected_row[
                    Constants.UI_TABLE_KEY_COL_LATEST_VERSION],
                Constants.UI_TABLE_KEY_COL_UNIQUE_VERSION: selected_row[
                    Constants.UI_TABLE_KEY_COL_UNIQUE_VERSION],
                Component.PINUP_MEDIA.value: selected_row[Component.PINUP_MEDIA.value],
                Component.PINUP_VIDEOS.value: selected_row[Component.PINUP_VIDEOS.value]
            }

            # Retrieve color
            row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                row=row
            )

            rows.append(row)

        # Create table
        self.__table = UITable(
            parent=tables_frame,
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
            self.__on_selected_version_changed
        )

        # Add a label to display the sub folder
        self.__sub_folder_label = tk.Label(
            info_frame,
            text=Context.get_text(
                'info_sub_folder',
                sub_folder='.'
            ),
            anchor=tk.W
        )
        self.__sub_folder_label.pack(
            fill=tk.X,
            padx=Constants.UI_PAD_BIG
        )

        # Add a listbox to display files and directories
        self.__listbox = tk.Listbox(
            info_frame,
            selectmode=tk.SINGLE,
            width=80,
            height=20
        )
        self.__listbox.pack(
            padx=Constants.UI_PAD_BIG,
            pady=Constants.UI_PAD_BIG
        )

        # Bind clicks
        self.__listbox.bind("<Button-3>", self.__show_context_menu)
        self.__listbox.bind("<Double-1>", self.__on_double_click)

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

        # Create components for rom
        info_rom_frame = tk.Frame(info_frame)
        info_rom_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            pady=Constants.UI_PAD_SMALL
        )
        info_rom_label = tk.Label(
            info_rom_frame,
            text=Context.get_text('info_rom')
        )
        info_rom_label.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.info_rom_entry_var = tk.StringVar()
        self.info_rom_entry_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.info_rom_entry = tk.Entry(
            info_rom_frame,
            textvariable=self.info_rom_entry_var,
            width=40
        )
        self.info_rom_entry.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )

        # Create components for videos path
        info_videos_path_frame = tk.Frame(info_frame)
        info_videos_path_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            pady=Constants.UI_PAD_SMALL
        )
        info_videos_path_label = tk.Label(
            info_videos_path_frame,
            text=Context.get_text('info_videos_path')
        )
        info_videos_path_label.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.info_videos_path_label = tk.Label(
            info_videos_path_frame
        )
        self.info_videos_path_label.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )

        # Create components for weblink1
        info_weblink1_frame = tk.Frame(info_frame)
        info_weblink1_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            pady=Constants.UI_PAD_SMALL
        )
        info_weblink1_label = tk.Label(
            info_weblink1_frame,
            text=Context.get_text('info_weblink1')
        )
        info_weblink1_label.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.info_weblink1_entry_var = tk.StringVar()
        self.info_weblink1_entry_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.info_weblink1_entry = tk.Entry(
            info_weblink1_frame,
            textvariable=self.info_weblink1_entry_var,
            width=40
        )
        self.info_weblink1_entry.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.button_open_weblink1 = tk.Button(
            info_weblink1_frame,
            text=Context.get_text(
                'target_action_open',
                target=Context.get_text('target_weblink')
            ),
            command=self.__open_weblink_1
        )
        self.button_open_weblink1.config(state=tk.DISABLED)
        self.button_open_weblink1.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )

        # Create components for weblink2
        info_weblink2_frame = tk.Frame(info_frame)
        info_weblink2_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            pady=Constants.UI_PAD_SMALL
        )
        info_weblink2_label = tk.Label(
            info_weblink2_frame,
            text=Context.get_text('info_weblink2')
        )
        info_weblink2_label.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.info_weblink2_entry_var = tk.StringVar()
        self.info_weblink2_entry_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.info_weblink2_entry = tk.Entry(
            info_weblink2_frame,
            textvariable=self.info_weblink2_entry_var,
            width=40
        )
        self.info_weblink2_entry.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.button_open_weblink2 = tk.Button(
            info_weblink2_frame,
            text=Context.get_text(
                'target_action_open',
                target=Context.get_text('target_weblink')
            ),
            command=self.__open_weblink_2
        )
        self.button_open_weblink2.config(state=tk.DISABLED)
        self.button_open_weblink2.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )

        if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:
            # Create components for emulator exe
            info_emulator_exe_frame = tk.Frame(info_frame)
            info_emulator_exe_frame.pack(
                side=tk.TOP,
                fill=tk.X,
                pady=Constants.UI_PAD_SMALL
            )
            info_emulator_exe_label = tk.Label(
                info_emulator_exe_frame,
                text=Context.get_text('info_emulator_exe')
            )
            info_emulator_exe_label.pack(
                side=tk.LEFT,
                padx=Constants.UI_PAD_SMALL
            )
            self.info_emulator_exe_combo_var = tk.StringVar()
            self.info_emulator_exe_combo_var.trace_add(
                "write",
                self.__on_entry_changed
            )
            self.info_emulator_exe_combo = ttk.Combobox(
                info_emulator_exe_frame,
                textvariable=self.info_emulator_exe_combo_var,
                width=40
            )
            self.info_emulator_exe_combo.pack(
                side=tk.LEFT,
                padx=Constants.UI_PAD_SMALL
            )
            self.info_emulator_exe_combo.bind(
                "<<ComboboxSelected>>",
                self.__on_entry_changed
            )

        # Create components for run mode
        info_run_mode_frame = tk.Frame(info_frame)
        info_run_mode_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            pady=Constants.UI_PAD_SMALL
        )
        info_run_mode_label = tk.Label(
            info_run_mode_frame,
            text=Context.get_text('info_run_mode')
        )
        info_run_mode_label.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.info_run_mode_entry_var = tk.StringVar()
        self.info_run_mode_entry_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.info_run_mode_entry = tk.Entry(
            info_run_mode_frame,
            textvariable=self.info_run_mode_entry_var,
            width=40
        )
        self.info_run_mode_entry.pack(
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

    def __get_selected_item_name(self):
        """Get selected item's name"""

        # Retrieved list's selection
        list_selection = self.__listbox.curselection()

        if not list_selection:
            return None

        selected_item = self.__listbox.get(list_selection[0])

        # Remove the icon
        item_name = selected_item.strip('📁 📄')

        return item_name

    def __get_selected_item_path(self):
        """Get selected item's path"""

        # Retrieved selected item's name
        selected_item_name = self.__get_selected_item_name()
        if selected_item_name is None or \
                selected_item_name == Context.get_text('info_parent_folder'):
            return self.__current_folder_path

        return os.path.join(
            self.__current_folder_path,
            selected_item_name
        )

    def __update_current_folder_path(self):
        """Update current folder's path"""

        # Retrieved selected item's name
        selected_item_name = self.__get_selected_item_name()

        # Do nothing if no selected item
        if selected_item_name is None:
            return

        if selected_item_name == Context.get_text('info_parent_folder'):
            self.__current_folder_path = os.path.dirname(
                self.__current_folder_path
            )
        else:
            self.__current_folder_path = os.path.join(
                self.__current_folder_path,
                selected_item_name
            )

    def __on_selected_version_changed(self, *args):
        """Called when selected version changed"""

        if self.__current_csv_item is None:
            return

        # Update buttons for version
        if self.__current_csv_item[Constants.CSV_COL_VERSION] != \
                self.info_current_version_combo.get():
            self.button_delete_version.config(state=tk.NORMAL)
        else:
            self.button_delete_version.config(state=tk.DISABLED)

        # Retrieve the version path
        self.__current_version_path = os.path.join(
            Context.get_working_path(),
            'tables',
            Context.get_selected_emulator().value,
            self.__current_item_id,
            self.info_current_version_combo.get()
        )

        # Retrieve the videos path
        self.__current_videos_path = os.path.join(
            Context.get_working_path(),
            'tables',
            Context.get_selected_emulator().value,
            self.__current_item_id,
            self.info_current_version_combo.get(),
            'PUPVideos'
        )

        videos_sub_directories = []
        if FileHelper.is_folder_exists(
            folder_path=self.__current_videos_path
        ):
            videos_sub_directories = FileHelper.list_sub_directories(
                folder_path=self.__current_videos_path
            )

        # Update videos path
        if len(videos_sub_directories) > 0:
            self.__current_csv_item[Constants.CSV_COL_VIDEOS_PATH] = videos_sub_directories[0]
        else:
            self.__current_csv_item[Constants.CSV_COL_VIDEOS_PATH] = None

        # Update info label for videos
        if BddHelper.is_not_null_value(self.__current_csv_item[Constants.CSV_COL_VIDEOS_PATH]):
            self.info_videos_path_label.config(
                text=self.__current_csv_item[Constants.CSV_COL_VIDEOS_PATH]
            )
        else:
            self.info_videos_path_label.config(
                text=''
            )

        # Reinitialize listbox
        self.__reinit_listbox()

        # Indicate that entry changed
        if args is not None and len(args) > 0:
            self.__on_entry_changed()

    def __on_entry_changed(self, *_):
        """Called when an entry changed"""

        self.button_cancel.config(state=tk.NORMAL)
        self.button_validate.config(state=tk.NORMAL)

        if WeblinkHelper.is_weblink(self.info_weblink1_entry_var.get()):
            self.button_open_weblink1.config(state=tk.NORMAL)
        else:
            self.button_open_weblink1.config(state=tk.DISABLED)

        if WeblinkHelper.is_weblink(self.info_weblink2_entry_var.get()):
            self.button_open_weblink2.config(state=tk.NORMAL)
        else:
            self.button_open_weblink2.config(state=tk.DISABLED)

    def __add_context_menu_command(
        self,
        context_menu: tk.Menu,
        label: str,
        command: any,
        add_separor_if_needed=False
    ):
        """Add a command in a Context Menu with an updated counter for commands"""

        if add_separor_if_needed and self.__context_menu_commands_count > 0:
            context_menu.add_separator()

        context_menu.add_command(label=label, command=command)
        self.__context_menu_commands_count += 1

    def __show_context_menu(self, event):
        """Called when right click on an item to show context menu"""

        self.__context_menu_commands_count = 0

        # Select nearest item
        item_idx = self.__listbox.nearest(event.y)
        self.__listbox.selection_clear(0, tk.END)
        self.__listbox.selection_set(item_idx)

        # Retrieved selected item's name and path
        selected_item_name = self.__get_selected_item_name()
        selected_item_path = self.__get_selected_item_path()

        # Build context menu
        context_menu = tk.Menu(self.__dialog, tearoff=0)

        if selected_item_name is not None and FileHelper.is_file_exists(
            file_path=selected_item_path
        ):
            # If selected path is a file

            # Retrieve file's extension
            _, file_extension = os.path.splitext(selected_item_path)

            if file_extension in Constants.VLC_SUPPORTED_EXTENSIONS:
                self.__add_context_menu_command(
                    context_menu=context_menu,
                    label=Context.get_text('media_action_open_vlc'),
                    command=self.__open_vlc_window
                )
            elif file_extension in Constants.PINUP_VIDEOS_BATCH_EXTENSIONS:
                self.__add_context_menu_command(
                    context_menu=context_menu,
                    label=Context.get_text(
                        'target_action_execute',
                        target=Context.get_text('target_batch')
                    ),
                    command=self.__execute_batch
                )

            self.__add_context_menu_command(
                context_menu=context_menu,
                label=Context.get_text(
                    'target_action_import',
                    target=Context.get_text('target_file')
                ),
                command=self.__import_file,
                add_separor_if_needed=True
            )

            self.__add_context_menu_command(
                context_menu=context_menu,
                label=Context.get_text(
                    'target_action_export',
                    target=Context.get_text('target_file')
                ),
                command=self.__export_file
            )

            self.__add_context_menu_command(
                context_menu=context_menu,
                label=Context.get_text(
                    'target_action_rename',
                    target=Context.get_text('target_file')
                ),
                command=self.__rename_file
            )

            self.__add_context_menu_command(
                context_menu=context_menu,
                label=Context.get_text(
                    'target_action_delete',
                    target=Context.get_text('target_file')
                ),
                command=self.__delete_file
            )

            self.__add_context_menu_command(
                context_menu=context_menu,
                label=Context.get_text(
                    'target_action_create',
                    target=Context.get_text('target_folder')
                ),
                command=self.__create_folder,
                add_separor_if_needed=True
            )

            self.__add_context_menu_command(
                context_menu=context_menu,
                label=Context.get_text(
                    'target_action_import',
                    target=Context.get_text('target_folder')
                ),
                command=self.__import_folder
            )

        elif selected_item_name is not None and FileHelper.is_folder_exists(
            folder_path=selected_item_path
        ):
            # If selected path is a folder

            self.__add_context_menu_command(
                context_menu=context_menu,
                label=Context.get_text(
                    'target_action_open',
                    target=Context.get_text('target_folder')
                ),
                command=self.__open_folder
            )
            self.__add_context_menu_command(
                context_menu=context_menu,
                label=Context.get_text(
                    'target_action_explore',
                    target=Context.get_text('target_folder')
                ),
                command=self.__explore_folder
            )

            if self.__current_folder_path != self.__current_videos_path:

                self.__add_context_menu_command(
                    context_menu=context_menu,
                    label=Context.get_text(
                        'target_action_import',
                        target=Context.get_text('target_file')
                    ),
                    command=self.__import_file,
                    add_separor_if_needed=True
                )

                self.__add_context_menu_command(
                    context_menu=context_menu,
                    label=Context.get_text(
                        'target_action_create',
                        target=Context.get_text('target_folder')
                    ),
                    command=self.__create_folder,
                    add_separor_if_needed=True
                )

                self.__add_context_menu_command(
                    context_menu=context_menu,
                    label=Context.get_text(
                        'target_action_import',
                        target=Context.get_text('target_folder')
                    ),
                    command=self.__import_folder
                )

                self.__add_context_menu_command(
                    context_menu=context_menu,
                    label=Context.get_text(
                        'target_action_export',
                        target=Context.get_text('target_folder')
                    ),
                    command=self.__export_folder
                )

                self.__add_context_menu_command(
                    context_menu=context_menu,
                    label=Context.get_text(
                        'target_action_rename',
                        target=Context.get_text('target_folder')
                    ),
                    command=self.__rename_folder
                )

                self.__add_context_menu_command(
                    context_menu=context_menu,
                    label=Context.get_text(
                        'target_action_delete',
                        target=Context.get_text('target_folder')
                    ),
                    command=self.__delete_folder
                )

        elif self.__current_folder_path != self.__current_videos_path:
            # If current path is not the current videos path
            self.__add_context_menu_command(
                context_menu=context_menu,
                label=Context.get_text(
                    'target_action_import',
                    target=Context.get_text('target_file')
                ),
                command=self.__import_file,
                add_separor_if_needed=True
            )

            self.__add_context_menu_command(
                context_menu=context_menu,
                label=Context.get_text(
                    'target_action_create',
                    target=Context.get_text('target_folder')
                ),
                command=self.__create_folder,
                add_separor_if_needed=True
            )

            self.__add_context_menu_command(
                context_menu=context_menu,
                label=Context.get_text(
                    'target_action_import',
                    target=Context.get_text('target_folder')
                ),
                command=self.__import_folder
            )

        if self.__current_folder_path == self.__current_version_path:
            # If current path is the current version path
            self.__add_context_menu_command(
                context_menu=context_menu,
                label=Context.get_text(
                    'target_action_import',
                    target=Context.get_text('target_video_pinup')
                ),
                command=self.__import_videos,
                add_separor_if_needed=True
            )
        elif self.__current_folder_path == self.__current_videos_path:
            # If current path is the current videos path
            self.__add_context_menu_command(
                context_menu=context_menu,
                label=Context.get_text(
                    'target_action_import',
                    target=Context.get_text('target_video_pinup')
                ),
                command=self.__import_videos,
                add_separor_if_needed=True
            )
            self.__add_context_menu_command(
                context_menu=context_menu,
                label=Context.get_text(
                    'target_action_export',
                    target=Context.get_text('target_video_pinup')
                ),
                command=self.__export_videos
            )
            self.__add_context_menu_command(
                context_menu=context_menu,
                label=Context.get_text(
                    'target_action_rename',
                    target=Context.get_text('target_video_pinup')
                ),
                command=self.__rename_videos
            )
            self.__add_context_menu_command(
                context_menu=context_menu,
                label=Context.get_text(
                    'target_action_delete',
                    target=Context.get_text('target_video_pinup')
                ),
                command=self.__delete_videos
            )

        # Show context menu in the mouse's position
        context_menu.post(event.x_root, event.y_root)

    def __on_double_click(self, event):
        """Called when double click on an item"""

        # Retrieved selected item's name and path
        selected_item_name = self.__get_selected_item_name()
        selected_item_path = self.__get_selected_item_path()

        # If selected path is a folder, open it
        if selected_item_name == Context.get_text('info_parent_folder') or \
                FileHelper.is_folder_exists(folder_path=selected_item_path):
            self.__open_folder()
        elif FileHelper.is_file_exists(
            file_path=selected_item_path
        ):
            # Retrieve file's extension
            _, file_extension = os.path.splitext(selected_item_path)

            if file_extension in Constants.VLC_SUPPORTED_EXTENSIONS:
                # Open the file if VLC file
                self.__open_vlc_window()
            elif file_extension in Constants.PINUP_VIDEOS_BATCH_EXTENSIONS:
                # Execute the file if batch
                self.__execute_batch()

    def __run_validate(self, should_interrupt):
        """Run validate"""

        # Flag item as modified
        self.__flag_item_as_modified()

        # Modify the table in the CSV
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

                # Retrieve new table folder
                new_table_folder = os.path.join(
                    Context.get_working_path(),
                    'tables',
                    Context.get_selected_emulator().value,
                    self.info_id_entry_var.get()
                )

                # Move the folder
                FileHelper.move_folder(
                    source_folder_path=os.path.join(
                        Context.get_working_path(),
                        'tables',
                        Context.get_selected_emulator().value,
                        csv_item[Constants.CSV_COL_ID]
                    ),
                    destination_folder_path=new_table_folder
                )

                # Rename all files
                for relative_path in FileHelper.list_relative_paths(
                    folder_path=new_table_folder,
                    file_name=f'{csv_item[Constants.CSV_COL_ID]}*'
                ):
                    if csv_item[Constants.CSV_COL_ID] not in relative_path:
                        continue

                    # Move the file
                    FileHelper.move_file(
                        source_file_path=os.path.join(
                            new_table_folder,
                            relative_path
                        ),
                        destination_file_path=os.path.join(
                            new_table_folder,
                            relative_path.replace(
                                csv_item[Constants.CSV_COL_ID],
                                self.info_id_entry_var.get()
                            )
                        )
                    )

                csv_item[Constants.CSV_COL_ID] = self.info_id_entry_var.get()

            # Check if run mode changed
            if csv_item[Constants.CSV_COL_ALT_RUN_MODE] != self.info_run_mode_entry_var.get():
                if BddHelper.is_not_null_value(self.info_run_mode_entry_var.get()):
                    csv_item[Constants.CSV_COL_ALT_RUN_MODE] = self.info_run_mode_entry_var.get(
                    )
                else:
                    csv_item[Constants.CSV_COL_ALT_RUN_MODE] = None

            # Check if rom changed
            if csv_item[Constants.CSV_COL_ROM] != self.info_rom_entry_var.get():
                if BddHelper.is_not_null_value(self.info_rom_entry_var.get()):
                    csv_item[Constants.CSV_COL_ROM] = self.info_rom_entry_var.get()
                else:
                    csv_item[Constants.CSV_COL_ROM] = None

            # Modify videos path
            csv_item[Constants.CSV_COL_VIDEOS_PATH] = \
                self.__current_csv_item[Constants.CSV_COL_VIDEOS_PATH]

            # Check if weblink1 changed
            if csv_item[Constants.CSV_COL_WEBLINK_URL] != self.info_weblink1_entry_var.get():
                if WeblinkHelper.is_weblink(url_text=self.info_weblink1_entry_var.get()):
                    csv_item[Constants.CSV_COL_WEBLINK_URL] = self.info_weblink1_entry_var.get(
                    )
                else:
                    csv_item[Constants.CSV_COL_WEBLINK_URL] = None

            # Check if weblink2 changed
            if csv_item[Constants.CSV_COL_WEBLINK2_URL] != self.info_weblink2_entry_var.get():
                if WeblinkHelper.is_weblink(url_text=self.info_weblink2_entry_var.get()):
                    csv_item[Constants.CSV_COL_WEBLINK2_URL] = self.info_weblink2_entry_var.get(
                    )
                else:
                    csv_item[Constants.CSV_COL_WEBLINK2_URL] = None

            # Check if available changed
            if csv_item[Constants.CSV_COL_AVAILABLE] != self.info_available_checkbox_var.get():
                if self.info_available_checkbox_var.get():
                    csv_item[Constants.CSV_COL_AVAILABLE] = Constants.CSV_YES_VALUE
                else:
                    csv_item[Constants.CSV_COL_AVAILABLE] = Constants.CSV_NO_VALUE

            if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X and \
                    csv_item[Constants.CSV_COL_ALT_EXE] != self.info_emulator_exe_combo.get():
                # Check if emulator exe changed
                csv_item[Constants.CSV_COL_ALT_EXE] = self.info_emulator_exe_combo.get()

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

                # Destroy Selenium Web Browser
                Context.destroy_selenium_web_browser()

                return

            if row in selected_rows:
                row[Constants.UI_TABLE_KEY_COL_ID] = self.__current_csv_item[
                    Constants.CSV_COL_ID]
                row[Constants.UI_TABLE_KEY_COL_NAME] = self.__current_csv_item[
                    Constants.CSV_COL_NAME]
                (row[Constants.UI_TABLE_KEY_COL_LATEST_VERSION],
                 row[Constants.UI_TABLE_KEY_COL_UNIQUE_VERSION]) = Verifier.verify_table_versions(
                    csv_table_id=self.__current_csv_item[Constants.CSV_COL_ID],
                    csv_table_weblink_url=self.__current_csv_item[Constants.CSV_COL_WEBLINK_URL]
                )
                row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                    row=row
                )
                break
            row_idx += 1

        # Destroy Selenium Web Browser
        Context.destroy_selenium_web_browser()

        self.__table.set_rows(
            rows=rows
        )

        # Select the table
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

    def __run_create_table(self, should_interrupt):
        """Run create a new table"""

        # Flag item as modified
        self.__flag_item_as_modified(
            item_id=self.new_table_id
        )

        # Create the media path
        os.makedirs(os.path.join(
            self.table_folder,
            self.new_table_version,
            'media'
        ))

        # Create the emulator path
        if Context.get_selected_emulator() == Emulator.FUTURE_PINBALL or \
                Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:
            os.makedirs(os.path.join(
                self.table_folder,
                self.new_table_version,
                'emulator',
                'Tables'
            ))

        # Add the table in the CSV
        csv_items = CsvHelper.read_data(
            file_path=Context.get_csv_path()
        )

        # Retrieve some info from current CSV Item
        alt_exe = None
        alt_run_mode = None
        if self.__current_csv_item is not None:
            alt_exe = self.__current_csv_item[Constants.CSV_COL_ALT_EXE]
            alt_run_mode = self.__current_csv_item[Constants.CSV_COL_ALT_RUN_MODE]

        csv_items.append({
            Constants.CSV_COL_AVAILABLE: Constants.CSV_YES_VALUE,
            Constants.CSV_COL_VERSION: self.new_table_version,
            Constants.CSV_COL_NAME: self.new_table_name,
            Constants.CSV_COL_ID: self.new_table_id,
            Constants.CSV_COL_ALT_EXE: alt_exe,
            Constants.CSV_COL_ALT_RUN_MODE: alt_run_mode,
            Constants.CSV_COL_ROM: None,
            Constants.CSV_COL_VIDEOS_PATH: None,
            Constants.CSV_COL_WEBLINK_URL: None,
            Constants.CSV_COL_WEBLINK2_URL: None
        })

        CsvHelper.write_data(
            file_path=Context.get_csv_path(),
            data=csv_items
        )

        # Change rows
        rows = self.__table.list_rows()
        row = {
            Constants.UI_TABLE_KEY_COL_SELECTION: False,
            Constants.UI_TABLE_KEY_COL_ID: self.new_table_id,
            Constants.UI_TABLE_KEY_COL_NAME: self.new_table_name
        }
        (row[Constants.UI_TABLE_KEY_COL_LATEST_VERSION],
            row[Constants.UI_TABLE_KEY_COL_UNIQUE_VERSION]) = Verifier.verify_table_versions(
            csv_table_id=self.new_table_id,
            csv_table_weblink_url=None
        )
        row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
            row=row
        )
        rows.insert(0, row)
        self.__table.set_rows(
            rows=rows
        )

        # Select the first table
        self.__table.set_selected_rows(
            rows_idx=[0]
        )

        # Destroy Selenium Web Browser
        Context.destroy_selenium_web_browser()

    def __create_table(self):
        """Create a new table"""

        # Ask an entry for the new table's id
        self.new_table_id = simpledialog.askstring(
            Context.get_text('confirmation'),
            Context.get_text(
                'confirm_create_table_1'
            ),
            parent=self.__dialog
        )

        if self.new_table_id is None:
            return

        # Retrieve the table's folder
        self.table_folder = os.path.join(
            Context.get_working_path(),
            'tables',
            Context.get_selected_emulator().value,
            self.new_table_id
        )

        # Check if table already exists
        if FileHelper.is_folder_exists(
            folder_path=self.table_folder
        ):
            messagebox.showerror(
                title=Context.get_text('error_title'),
                message=Context.get_text(
                    'error_table_already_exists',
                    table=self.new_table_id
                ),
                parent=self.__dialog
            )
            return

        # Ask an entry for the new table's name
        self.new_table_name = simpledialog.askstring(
            Context.get_text('confirmation'),
            Context.get_text(
                'confirm_create_table_2'
            ),
            parent=self.__dialog
        )

        if self.new_table_name is None:
            return

        # First letter has to be an uppercase for the name
        self.new_table_name = self.new_table_name[0].upper(
        ) + self.new_table_name[1:]

        # Ask an entry for the new version
        while True:
            self.new_table_version = simpledialog.askstring(
                Context.get_text('confirmation'),
                Context.get_text(
                    'confirm_create_table_3'
                ),
                parent=self.__dialog
            )
            if self.new_table_version is None:
                break
            if re.fullmatch(r"[a-zA-Z0-9.]+", self.new_table_version):
                break

        if self.new_table_version is None:
            return

        # Execute the process in a waiting dialog
        WaitingDialog(
            parent=self.__dialog,
            process_name=Context.get_text('process_creation'),
            process_function=self.__run_create_table
        )

    def __run_delete_table(self, should_interrupt):
        """Run delete a table"""

        # Flag item as modified
        self.__flag_item_as_modified()

        # Delete the folder
        FileHelper.delete_folder(
            folder_path=os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
                self.__current_item_id
            )
        )

        # Remove the table from the CSV
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

        # Select the first table
        self.__table.set_selected_rows(
            rows_idx=[0]
        )

    def __delete_table(self):
        """Delete a table"""

        # Ask a confirmation to delete
        if not messagebox.askokcancel(
            Context.get_text('confirmation'),
            Context.get_text(
                'confirm_delete_table',
                table=self.__current_csv_item[Constants.CSV_COL_NAME]
            ),
            parent=self.__dialog
        ):
            return

        # Execute the process in a waiting dialog
        WaitingDialog(
            parent=self.__dialog,
            process_name=Context.get_text('process_deletion'),
            process_function=self.__run_delete_table
        )

    def __run_create_version(self, should_interrupt):
        """Run create a new version"""

        # Flag item as modified
        self.__flag_item_as_modified()

        # Copy folder to the new version
        FileHelper.copy_folder(
            source_folder_path=os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
                self.__current_item_id,
                self.info_current_version_combo.get()
            ),
            destination_folder_path=os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
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

                # Destroy Selenium Web Browser
                Context.destroy_selenium_web_browser()

                return

            if row[Constants.UI_TABLE_KEY_COL_ID] == self.__current_csv_item[Constants.CSV_COL_ID]:
                (row[Constants.UI_TABLE_KEY_COL_LATEST_VERSION],
                 row[Constants.UI_TABLE_KEY_COL_UNIQUE_VERSION]) = Verifier.verify_table_versions(
                    csv_table_id=self.__current_csv_item[Constants.CSV_COL_ID],
                    csv_table_weblink_url=self.__current_csv_item[Constants.CSV_COL_WEBLINK_URL]
                )
                row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                    row=row
                )
                break
            row_idx += 1

        # Destroy Selenium Web Browser
        Context.destroy_selenium_web_browser()

        self.__table.set_rows(
            rows=rows
        )
        self.__table.set_selected_rows(
            rows_idx=[row_idx]
        )

        # Advise that selected version changed
        self.__on_selected_version_changed()

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

        # Flag item as modified
        self.__flag_item_as_modified()

        # Move folder to the new version
        FileHelper.move_folder(
            source_folder_path=os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
                self.__current_item_id,
                self.info_current_version_combo.get()
            ),
            destination_folder_path=os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
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

        # Change rows
        rows = self.__table.list_rows()
        row_idx = 0
        for row in rows:

            if should_interrupt():

                # Destroy Selenium Web Browser
                Context.destroy_selenium_web_browser()

                return

            if row[Constants.UI_TABLE_KEY_COL_ID] == self.__current_csv_item[Constants.CSV_COL_ID]:
                (row[Constants.UI_TABLE_KEY_COL_LATEST_VERSION],
                 row[Constants.UI_TABLE_KEY_COL_UNIQUE_VERSION]) = Verifier.verify_table_versions(
                    csv_table_id=self.__current_csv_item[Constants.CSV_COL_ID],
                    csv_table_weblink_url=self.__current_csv_item[Constants.CSV_COL_WEBLINK_URL]
                )
                row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                    row=row
                )
                break
            row_idx += 1

        # Destroy Selenium Web Browser
        Context.destroy_selenium_web_browser()

        self.__table.set_rows(
            rows=rows
        )
        self.__table.set_selected_rows(
            rows_idx=[row_idx]
        )

        # Advise that selected version changed
        self.__on_selected_version_changed()

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

        # Flag item as modified
        self.__flag_item_as_modified()

        # Delete the folder
        FileHelper.delete_folder(
            folder_path=os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
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

                # Destroy Selenium Web Browser
                Context.destroy_selenium_web_browser()

                return

            if row[Constants.UI_TABLE_KEY_COL_ID] == self.__current_csv_item[Constants.CSV_COL_ID]:
                (row[Constants.UI_TABLE_KEY_COL_LATEST_VERSION],
                 row[Constants.UI_TABLE_KEY_COL_UNIQUE_VERSION]) = Verifier.verify_table_versions(
                    csv_table_id=self.__current_csv_item[Constants.CSV_COL_ID],
                    csv_table_weblink_url=self.__current_csv_item[Constants.CSV_COL_WEBLINK_URL]
                )
                row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                    row=row
                )
                break
            row_idx += 1

        # Destroy Selenium Web Browser
        Context.destroy_selenium_web_browser()

        self.__table.set_rows(
            rows=rows
        )
        self.__table.set_selected_rows(
            rows_idx=[row_idx]
        )

        # Advise that selected version changed
        self.__on_selected_version_changed()

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

    def __open_weblink_1(self):
        """Open the first weblink"""

        WeblinkHelper.open_weblink(self.info_weblink1_entry_var.get())

    def __open_weblink_2(self):
        """Open the second weblink"""

        WeblinkHelper.open_weblink(self.info_weblink2_entry_var.get())

    def __explore_version(self):
        """Explore the folder for a version"""

        FileHelper.explore_folder(
            folder_path=self.__current_version_path
        )

    def __init_info_entries(self):
        """Initialize info entries"""

        # Retrieve item from CSV
        self.__current_csv_item = ListHelper.select_item(
            item_id=self.__current_item_id,
            a_list=CsvHelper.read_data(
                file_path=Context.get_csv_path()
            ),
            id_column=Constants.CSV_COL_ID
        )

        # Retrieve item's version
        item_version = self.__current_csv_item.get(
            Constants.CSV_COL_VERSION,
            Constants.LATEST_PATH
        )

        # Retrieve all versions and current version
        all_versions = FileHelper.list_sub_directories(
            folder_path=os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
                self.__current_item_id
            )
        )

        # Update versions components
        self.info_current_version_combo.config(
            values=all_versions
        )
        self.info_current_version_combo.set(item_version)

        # Update entries components
        self.info_id_entry_var.set(
            self.__current_csv_item[Constants.CSV_COL_ID]
        )

        self.info_name_entry_var.set(
            self.__current_csv_item[Constants.CSV_COL_NAME]
        )

        if BddHelper.is_not_null_value(self.__current_csv_item[Constants.CSV_COL_ALT_RUN_MODE]):
            self.info_run_mode_entry_var.set(
                self.__current_csv_item[Constants.CSV_COL_ALT_RUN_MODE]
            )
        else:
            self.info_run_mode_entry_var.set('')

        if BddHelper.is_not_null_value(self.__current_csv_item[Constants.CSV_COL_ROM]):
            self.info_rom_entry_var.set(
                self.__current_csv_item[Constants.CSV_COL_ROM]
            )
        else:
            self.info_rom_entry_var.set('')

        if BddHelper.is_not_null_value(self.__current_csv_item[Constants.CSV_COL_VIDEOS_PATH]):
            self.info_videos_path_label.config(
                text=self.__current_csv_item[Constants.CSV_COL_VIDEOS_PATH]
            )
        else:
            self.info_videos_path_label.config(
                text=''
            )

        if BddHelper.is_not_null_value(self.__current_csv_item[Constants.CSV_COL_WEBLINK_URL]):
            self.info_weblink1_entry_var.set(
                self.__current_csv_item[Constants.CSV_COL_WEBLINK_URL]
            )
        else:
            self.info_weblink1_entry_var.set('')

        if BddHelper.is_not_null_value(self.__current_csv_item[Constants.CSV_COL_WEBLINK2_URL]):
            self.info_weblink2_entry_var.set(
                self.__current_csv_item[Constants.CSV_COL_WEBLINK2_URL]
            )
        else:
            self.info_weblink2_entry_var.set('')

        if self.__current_csv_item[Constants.CSV_COL_AVAILABLE] == Constants.CSV_YES_VALUE:
            self.info_available_checkbox_var.set(True)
        else:
            self.info_available_checkbox_var.set(False)

        if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:

            # Retrieve all emulator exe
            all_emulator_exe = []
            for a_csv_item in CsvHelper.read_data(
                file_path=Context.get_csv_path()
            ):
                if a_csv_item[Constants.CSV_COL_ALT_EXE] not in all_emulator_exe:
                    all_emulator_exe.append(
                        a_csv_item[Constants.CSV_COL_ALT_EXE])

            # Update entries for VPX
            self.info_emulator_exe_combo.config(
                values=all_emulator_exe
            )
            self.info_emulator_exe_combo.set(
                self.__current_csv_item[Constants.CSV_COL_ALT_EXE]
            )

        # Disable buttons to cancel or validate
        self.button_cancel.config(state=tk.DISABLED)
        self.button_validate.config(state=tk.DISABLED)
        self.button_create_version.config(state=tk.NORMAL)

        # Advise that selected version changed
        self.__on_selected_version_changed()

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

        # Initialize info entries
        self.__init_info_entries()

    def __flag_item_as_modified(
        self,
        item_id=None
    ):
        """Flag the item as modified. If no item, current item is concerned"""

        if item_id is None:
            item_id = self.__current_item_id

        if item_id not in self.__modified_ids:
            self.__modified_ids.append(item_id)

    def __on_close(self):
        """Called when closing"""

        # Call back if some modifications done
        if len(self.__modified_ids) > 0:
            self.__callback(
                only_ids=self.__modified_ids
            )

        # Close VLC
        self.__close_vlc_window()

        # Close the dialog
        UIHelper.close_dialog(self.__dialog)

    def __open_vlc_window(self):
        """Open the current media in a VLC window"""

        # Close VLC window if already open
        self.__close_vlc_window()

        # Initialize a new media player for the window
        self.__vlc_media_player = self.__vlc_instance.media_player_new(
            self.__get_selected_item_path()
        )

        # Create a new tkinter window
        self.__vlc_window = tk.Toplevel(self.__dialog)
        self.__vlc_window.title(Context.get_text('media_title'))
        self.__vlc_window.geometry("800x600")

        # Attach the video to the handle of the new window
        self.__vlc_window.update_idletasks()
        self.__vlc_media_player.set_hwnd(self.__vlc_window.winfo_id())

        # Play the video in the new window
        self.__vlc_media_player.play()

        # Add an action to exit fullscreen mode
        self.__vlc_window.bind(
            '<Escape>', lambda event: self.__close_vlc_window()
        )

        # Handle the window's close button (top-right 'X')
        self.__vlc_window.protocol("WM_DELETE_WINDOW", self.__close_vlc_window)

        # Set focus to the new window
        self.__vlc_window.focus_set()  # Set focus to the new window

        # Bring the window to the top of the stack
        self.__vlc_window.lift()

    def __close_vlc_window(self):
        """Close VLC window"""

        if self.__vlc_window is not None:
            self.__vlc_media_player.stop()
            self.__vlc_window.destroy()
            self.__vlc_window = None

    def __create_folder(self):
        """Create a folder"""

        # Ask an entry for the new name
        self.new_name = simpledialog.askstring(
            Context.get_text('confirmation'),
            Context.get_text('confirm_create_folder'),
            parent=self.__dialog
        )

        if self.new_name is None:
            return

        # Execute the creation in a waiting dialog
        WaitingDialog(
            parent=self.__dialog,
            process_name=Context.get_text('process_creation'),
            process_function=self.__run_create_folder
        )

    def __run_create_folder(self, should_interrupt):
        """Run create folder"""

        # Flag item as modified
        self.__flag_item_as_modified()

        # Create the folder
        FileHelper.create_folder(
            folder_path=os.path.join(
                self.__current_folder_path,
                self.new_name
            )
        )

        # Reinitialize listbox
        self.__reinit_listbox(
            folder_path=self.__current_folder_path
        )

    def __explore_folder(self):
        """Explore a folder in Windows Explorer"""

        FileHelper.explore_folder(
            folder_path=self.__get_selected_item_path()
        )

    def __import_file(self):
        """Import a file"""

        # Ask source file's path
        self.__source_file_path = filedialog.askopenfilename(
            parent=self.__dialog
        )

        if not self.__source_file_path:
            return

        # Ask if table's name keeping
        self.__keep_table_name = messagebox.askyesno(
            Context.get_text('question'),
            Context.get_text('question_rename_file_with_table_name'),
            parent=self.__dialog
        )

        # Execute the import in a waiting dialog
        WaitingDialog(
            parent=self.__dialog,
            process_name=Context.get_text('process_importation'),
            process_function=self.__run_import_file
        )

    def __run_import_file(self, should_interrupt):
        """Run import file"""

        # Flag item as modified
        self.__flag_item_as_modified()

        # Retrieve new file path's name
        if self.__keep_table_name:

            # Retrieve file's extension
            _, file_extension = os.path.splitext(
                self.__source_file_path
            )

            new_file_name = self.__current_item_id + file_extension
        else:
            new_file_name = os.path.basename(
                self.__source_file_path
            )

        # Import the new file
        FileHelper.copy_file(
            source_file_path=self.__source_file_path,
            destination_file_path=os.path.join(
                self.__current_folder_path,
                new_file_name
            )
        )

        # Reinitialize listbox
        self.__reinit_listbox(
            folder_path=self.__current_folder_path
        )

    def __import_folder(self):
        """Import a folder"""

        # Ask source folder's path
        self.__source_folder_path = filedialog.askdirectory(
            parent=self.__dialog
        )

        if not self.__source_folder_path:
            return

        # Execute the import in a waiting dialog
        WaitingDialog(
            parent=self.__dialog,
            process_name=Context.get_text('process_importation'),
            process_function=self.__run_import_folder
        )

    def __run_import_folder(self, should_interrupt):
        """Run import folder"""

        # Flag item as modified
        self.__flag_item_as_modified()

        # Retrieve new folder path's name
        new_folder_name = os.path.basename(
            self.__source_folder_path
        )

        # Import the new folder
        FileHelper.copy_folder(
            source_folder_path=self.__source_folder_path,
            destination_folder_path=os.path.join(
                self.__current_folder_path,
                new_folder_name
            )
        )

        # Reinitialize listbox
        self.__reinit_listbox(
            folder_path=self.__current_folder_path
        )

    def __import_videos(self):
        """Import videos"""

        # Ask source folder's path
        self.__source_folder_path = filedialog.askdirectory(
            parent=self.__dialog
        )
        if self.__source_folder_path:

            # Execute the import in a waiting dialog
            WaitingDialog(
                parent=self.__dialog,
                process_name=Context.get_text('process_importation'),
                process_function=self.__run_import_videos
            )

    def __run_import_videos(self, should_interrupt):
        """Run import videos"""

        # Flag item as modified
        self.__flag_item_as_modified()

        # Retrieve new videos path's name
        new_videos_path_name = os.path.basename(
            self.__source_folder_path
        )

        # Delete the current videos
        FileHelper.delete_folder(
            folder_path=self.__current_videos_path
        )

        # Import the new videos
        FileHelper.copy_folder(
            source_folder_path=self.__source_folder_path,
            destination_folder_path=os.path.join(
                self.__current_videos_path,
                new_videos_path_name
            )
        )

        # Update selected CSV item
        self.__current_csv_item[Constants.CSV_COL_VIDEOS_PATH] = new_videos_path_name

        # Update info label for videos
        self.info_videos_path_label.config(
            text=self.__current_csv_item[Constants.CSV_COL_VIDEOS_PATH]
        )

        # Reinitialize listbox
        self.__reinit_listbox(
            folder_path=self.__current_folder_path
        )

        # Indicate that entry changed
        self.__on_entry_changed()

    def __export_file(self):
        """Export a file"""

        # Ask destination folder's path
        destination_folder_path = filedialog.askdirectory(
            parent=self.__dialog
        )
        if destination_folder_path:

            self.__destination_file_path = os.path.join(
                destination_folder_path,
                self.__get_selected_item_name()
            )

            # Execute the export in a waiting dialog
            WaitingDialog(
                parent=self.__dialog,
                process_name=Context.get_text('process_exportation'),
                process_function=self.__run_export_file
            )

    def __run_export_file(self, should_interrupt):
        """Run export file"""

        # Export the file
        FileHelper.copy_file(
            source_file_path=self.__get_selected_item_path(),
            destination_file_path=self.__destination_file_path
        )

    def __export_folder(self):
        """Export a folder"""

        # Ask destination folder's path
        destination_folder_path = filedialog.askdirectory(
            parent=self.__dialog
        )
        if destination_folder_path:

            self.__destination_folder_path = os.path.join(
                destination_folder_path,
                self.__get_selected_item_name()
            )

            # Execute the export in a waiting dialog
            WaitingDialog(
                parent=self.__dialog,
                process_name=Context.get_text('process_exportation'),
                process_function=self.__run_export_folder
            )

    def __run_export_folder(self, should_interrupt):
        """Run export folder"""

        # Export the folder
        FileHelper.copy_folder(
            source_folder_path=self.__get_selected_item_path(),
            destination_folder_path=self.__destination_folder_path
        )

    def __export_videos(self):
        """Export videos"""

        # Ask destination folder's path
        destination_folder_path = filedialog.askdirectory(
            parent=self.__dialog
        )
        if destination_folder_path:

            self.__destination_folder_path = os.path.join(
                destination_folder_path,
                self.__current_csv_item[Constants.CSV_COL_VIDEOS_PATH]
            )

            # Execute the export in a waiting dialog
            WaitingDialog(
                parent=self.__dialog,
                process_name=Context.get_text('process_exportation'),
                process_function=self.__run_export_videos
            )

    def __run_export_videos(self, should_interrupt):
        """Run export videos"""

        # Export the videos folder
        FileHelper.copy_folder(
            source_folder_path=os.path.join(
                self.__current_videos_path,
                self.__current_csv_item[Constants.CSV_COL_VIDEOS_PATH]
            ),
            destination_folder_path=self.__destination_folder_path
        )

    def __delete_file(self):
        """Delete a file"""

        if messagebox.askokcancel(
            Context.get_text('confirmation'),
            Context.get_text('confirm_delete_file'),
            parent=self.__dialog
        ):

            # Execute the delete in a waiting dialog
            WaitingDialog(
                parent=self.__dialog,
                process_name=Context.get_text('process_deletion'),
                process_function=self.__run_delete_file
            )

    def __run_delete_file(self, should_interrupt):
        """Run delete file"""

        # Flag item as modified
        self.__flag_item_as_modified()

        # Delete the current file
        FileHelper.delete_file(
            file_path=self.__get_selected_item_path()
        )

        # Reinitialize listbox
        self.__reinit_listbox(
            folder_path=self.__current_folder_path
        )

    def __delete_folder(self):
        """Delete a folder"""

        if messagebox.askokcancel(
            Context.get_text('confirmation'),
            Context.get_text('confirm_delete_folder'),
            parent=self.__dialog
        ):

            # Execute the delete in a waiting dialog
            WaitingDialog(
                parent=self.__dialog,
                process_name=Context.get_text('process_deletion'),
                process_function=self.__run_delete_folder
            )

    def __run_delete_folder(self, should_interrupt):
        """Run delete folder"""

        # Flag item as modified
        self.__flag_item_as_modified()

        # Delete the current folder
        FileHelper.delete_folder(
            folder_path=self.__get_selected_item_path()
        )

        # Reinitialize listbox
        self.__reinit_listbox(
            folder_path=self.__current_folder_path
        )

    def __delete_videos(self):
        """Delete videos"""

        if messagebox.askokcancel(
            Context.get_text('confirmation'),
            Context.get_text('confirm_delete_videos'),
            parent=self.__dialog
        ):

            # Execute the delete in a waiting dialog
            WaitingDialog(
                parent=self.__dialog,
                process_name=Context.get_text('process_deletion'),
                process_function=self.__run_delete_videos
            )

    def __run_delete_videos(self, should_interrupt):
        """Run delete videos"""

        # Flag item as modified
        self.__flag_item_as_modified()

        # Delete the current videos
        FileHelper.delete_folder(
            folder_path=self.__current_videos_path
        )

        # Update selected CSV item
        self.__current_csv_item[Constants.CSV_COL_VIDEOS_PATH] = None

        # Update info label for videos
        self.info_videos_path_label.config(
            text=''
        )

        # Reinitialize listbox
        self.__reinit_listbox(
            folder_path=self.__current_folder_path
        )

        # Indicate that entry changed
        self.__on_entry_changed()

    def __rename_file(self):
        """Rename a file"""

        # Ask an entry for the new name
        self.new_name = simpledialog.askstring(
            Context.get_text('confirmation'),
            Context.get_text('confirm_rename'),
            parent=self.__dialog
        )

        if self.new_name is None:
            return

        # Execute the rename in a waiting dialog
        WaitingDialog(
            parent=self.__dialog,
            process_name=Context.get_text('process_renaming'),
            process_function=self.__run_rename_file
        )

    def __run_rename_file(self, should_interrupt):
        """Run rename file"""

        # Flag item as modified
        self.__flag_item_as_modified()

        # Rename the file
        FileHelper.move_file(
            source_file_path=self.__get_selected_item_path(),
            destination_file_path=os.path.join(
                self.__current_folder_path,
                self.new_name
            )
        )

        # Reinitialize listbox
        self.__reinit_listbox(
            folder_path=self.__current_folder_path
        )

    def __rename_folder(self):
        """Rename a folder"""

        # Ask an entry for the new name
        self.new_name = simpledialog.askstring(
            Context.get_text('confirmation'),
            Context.get_text('confirm_rename'),
            parent=self.__dialog
        )

        if self.new_name is None:
            return

        # Execute the rename in a waiting dialog
        WaitingDialog(
            parent=self.__dialog,
            process_name=Context.get_text('process_renaming'),
            process_function=self.__run_rename_folder
        )

    def __run_rename_folder(self, should_interrupt):
        """Run rename folder"""

        # Flag item as modified
        self.__flag_item_as_modified()

        # Rename the folder
        FileHelper.move_folder(
            source_folder_path=self.__get_selected_item_path(),
            destination_folder_path=os.path.join(
                self.__current_folder_path,
                self.new_name
            )
        )

        # Reinitialize listbox
        self.__reinit_listbox(
            folder_path=self.__current_folder_path
        )

    def __rename_videos(self):
        """Rename videos"""

        # Ask an entry for the new name
        self.new_videos_path_name = simpledialog.askstring(
            Context.get_text('confirmation'),
            Context.get_text('confirm_rename'),
            parent=self.__dialog
        )

        if self.new_videos_path_name is None:
            return

        # Execute the rename in a waiting dialog
        WaitingDialog(
            parent=self.__dialog,
            process_name=Context.get_text('process_renaming'),
            process_function=self.__run_rename_videos
        )

    def __run_rename_videos(self, should_interrupt):
        """Run rename videos"""

        # Flag item as modified
        self.__flag_item_as_modified()

        # Rename the current videos path
        FileHelper.move_folder(
            source_folder_path=os.path.join(
                self.__current_videos_path,
                self.__get_selected_item_name()
            ),
            destination_folder_path=os.path.join(
                self.__current_videos_path,
                self.new_videos_path_name
            )
        )

        # Update selected CSV item
        self.__current_csv_item[Constants.CSV_COL_VIDEOS_PATH] = self.new_videos_path_name

        # Update info label for videos
        self.info_videos_path_label.config(
            text=self.__current_csv_item[Constants.CSV_COL_VIDEOS_PATH]
        )

        # Reinitialize listbox
        self.__reinit_listbox(
            folder_path=self.__current_folder_path
        )

        # Indicate that entry changed
        self.__on_entry_changed()

    def __execute_batch(self):
        """Execute the Batch"""

        if messagebox.askokcancel(
            Context.get_text('confirmation'),
            Context.get_text('confirm_execute_batch'),
            parent=self.__dialog
        ):

            # Execute the batch in a waiting dialog
            WaitingDialog(
                parent=self.__dialog,
                process_name=Context.get_text('process_execution'),
                process_function=self.__run_execute_batch
            )

    def __run_execute_batch(self, should_interrupt):
        """Run execute the Batch"""

        # Flag item as modified
        self.__flag_item_as_modified()

        # Execute the batch with a timeout of 10 seconds
        CmdHelper.run(
            self.__get_selected_item_path(),
            check=False,
            timeout=10
        )

        # Reinitialize listbox
        self.__reinit_listbox(
            folder_path=self.__current_folder_path
        )

    def __reinit_listbox(
        self,
        folder_path=None
    ):
        """Reinitialize listbox"""

        # Remove selection
        self.__listbox.selection_clear(0, tk.END)

        if folder_path is None:
            # Reinitialize current folder with version path
            self.__current_folder_path = self.__current_version_path
        else:
            # Reinitialize current folder with folder specified
            self.__current_folder_path = folder_path

        # Open folder
        self.__open_folder()

    def __open_folder(self):
        """Open a folder"""

        # Update selected path
        self.__update_current_folder_path()

        # Reinitialize the listbox
        self.__listbox.delete(0, tk.END)
        self.__listbox.selection_clear(0, tk.END)

        if FileHelper.is_folder_exists(
            folder_path=self.__current_folder_path
        ):
            # Show item for parent folder if sub folder
            if self.__current_folder_path != self.__current_version_path:
                self.__listbox.insert(
                    tk.END,
                    Context.get_text('info_parent_folder')
                )

            # Show files then folders
            items = FileHelper.list_sub_directories(
                folder_path=self.__current_folder_path
            )
            files = []
            folders = []

            for item in items:
                item_path = os.path.join(self.__current_folder_path, item)
                if os.path.isdir(item_path):
                    folders.append(item)
                else:
                    files.append(item)

            for folder in folders:
                self.__listbox.insert(
                    tk.END,
                    f"📁 {folder}"
                )
            for file in files:
                self.__listbox.insert(
                    tk.END,
                    f"📄 {file}"
                )

            # Update label for sub folder
            self.__sub_folder_label.config(
                text=Context.get_text(
                    'info_sub_folder',
                    sub_folder=os.path.relpath(
                        self.__current_folder_path,
                        self.__current_version_path
                    )
                )
            )
