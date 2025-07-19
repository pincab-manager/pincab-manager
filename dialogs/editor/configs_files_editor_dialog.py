#!/usr/bin/python3
"""Dialog to edit configs files"""

import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
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


class ConfigsFilesEditorDialog:
    """Dialog to edit configs files"""

    def __init__(
        self,
        parent,
        callback
    ):
        """Initialize dialog"""

        self.__callback = callback
        self.__table = None
        self.__current_item_id = None
        self.__current_item_folder_path = None
        self.__current_folder_path = None
        self.__context_menu_commands_count = 0

        # Create dialog
        self.__dialog = tk.Toplevel(parent)

        # Fix dialog's title
        self.__dialog.title(Context.get_text('edit_configs_files'))

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

        # Bind closing event
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
            fill=tk.BOTH,
            padx=Constants.UI_PAD_BIG,
            pady=Constants.UI_PAD_BIG
        )

        # Bind clicks
        self.__listbox.bind("<Button-3>", self.__show_context_menu)
        self.__listbox.bind("<Double-1>", self.__on_double_click)

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

        if selected_item_name is None or \
                selected_item_name == Context.get_text('info_parent_folder'):

            # If no selected path

            self.__add_context_menu_command(
                context_menu=context_menu,
                label=Context.get_text(
                    'target_action_explore',
                    target=Context.get_text('target_folder')
                ),
                command=self.__explore_folder
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

        elif FileHelper.is_file_exists(
            file_path=selected_item_path
        ):
            # If selected path is a file
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

        elif FileHelper.is_folder_exists(
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

    def __run_create_config(self, should_interrupt):
        """Run create a new config"""

        # Create the config path
        os.makedirs(os.path.join(
            Context.get_configs_path(),
            self.new_config,
            Component.FILES.name.lower()
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

        # Set current folder
        self.__current_item_folder_path = os.path.join(
            Context.get_configs_path(),
            self.__current_item_id,
            Component.FILES.name.lower()
        )

        # Reinitialize listbox
        self.__reinit_listbox(
            folder_path=self.__current_item_folder_path
        )

    def __on_close(self):
        """Called when closing"""

        # Call back
        self.__callback()

        # Close the dialog
        UIHelper.close_dialog(self.__dialog)

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

        # Ask if keep absolute path
        self.__keep_absolute_path = messagebox.askyesno(
            Context.get_text('question'),
            Context.get_text(
                'question_keep_absolute_path',
                path=self.__source_file_path
            ),
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

        # Retrieve new file's name
        new_file_name = os.path.basename(
            self.__source_file_path
        )

        # Keep or not the absolute path
        if self.__keep_absolute_path:
            full_path = Path(self.__source_file_path).parent
            destination_file_path = os.path.join(
                self.__current_item_folder_path,
                full_path.relative_to(full_path.drive + '\\')
            )
            os.makedirs(destination_file_path)
            new_current_folder_path = self.__current_item_folder_path
        else:
            destination_file_path = os.path.join(
                self.__current_folder_path,
                new_file_name
            )
            new_current_folder_path = self.__current_folder_path

        # Import the new file
        FileHelper.copy_file(
            source_file_path=self.__source_file_path,
            destination_file_path=destination_file_path
        )

        # Reinitialize listbox
        self.__reinit_listbox(
            folder_path=new_current_folder_path
        )

    def __import_folder(self):
        """Import a folder"""

        # Ask source folder's path
        self.__source_folder_path = filedialog.askdirectory(
            parent=self.__dialog
        )

        if not self.__source_folder_path:
            return

        # Ask if keep absolute path
        self.__keep_absolute_path = messagebox.askyesno(
            Context.get_text('question'),
            Context.get_text(
                'question_keep_absolute_path',
                path=self.__source_folder_path
            ),
            parent=self.__dialog
        )

        # Execute the import in a waiting dialog
        WaitingDialog(
            parent=self.__dialog,
            process_name=Context.get_text('process_importation'),
            process_function=self.__run_import_folder
        )

    def __run_import_folder(self, should_interrupt):
        """Run import folder"""

        # Retrieve new folder's name
        new_folder_name = os.path.basename(
            self.__source_folder_path
        )

        # Keep or not the absolute path
        if self.__keep_absolute_path:
            full_path = Path(self.__source_folder_path)
            destination_folder_path = os.path.join(
                self.__current_item_folder_path,
                full_path.relative_to(full_path.drive + '\\')
            )
            new_current_folder_path = self.__current_item_folder_path
        else:
            destination_folder_path = os.path.join(
                self.__current_folder_path,
                new_folder_name
            )
            new_current_folder_path = self.__current_folder_path

        # Import the new folder
        FileHelper.copy_folder(
            source_folder_path=self.__source_folder_path,
            destination_folder_path=destination_folder_path
        )

        # Reinitialize listbox
        self.__reinit_listbox(
            folder_path=new_current_folder_path
        )

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

        # Delete the current folder
        FileHelper.delete_folder(
            folder_path=self.__get_selected_item_path()
        )

        # Reinitialize listbox
        self.__reinit_listbox(
            folder_path=self.__current_folder_path
        )

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

    def __reinit_listbox(
        self,
        folder_path=None
    ):
        """Reinitialize listbox"""

        # Remove selection
        self.__listbox.selection_clear(0, tk.END)

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
            # Show item for parent folder
            if self.__current_item_folder_path != self.__current_folder_path:
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

            for file in files:
                self.__listbox.insert(
                    tk.END,
                    f"📄 {file}"
                )
            for folder in folders:
                self.__listbox.insert(
                    tk.END,
                    f"📁 {folder}"
                )

            # Update label for sub folder
            self.__sub_folder_label.config(
                text=Context.get_text(
                    'info_sub_folder',
                    sub_folder=os.path.relpath(
                        self.__current_folder_path,
                        start=self.__current_item_folder_path
                    )
                )
            )
