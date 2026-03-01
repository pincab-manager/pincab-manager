#!/usr/bin/python3
"""Dialog to select a registry key"""

import tkinter as tk

from libraries.constants.constants import Constants
from libraries.context.context import Context
from libraries.ui.ui_helper import UIHelper
from libraries.winreg.winreg_helper import WinRegHelper

# pylint: disable=too-many-instance-attributes
# pylint: disable=unused-argument


class RegistryKeySelectorDialog:
    """Dialog to select a registry key"""

    def __init__(
        self,
        parent,
        callback
    ):
        """Initialize dialog"""

        self.__callback = callback
        self.__current_key = ''
        self.__context_menu_commands_count = 0

        # Get all users keys in a tree
        self.__registry_keys_tree = WinRegHelper.get_user_keys_tree()

        # Create dialog
        self.__dialog = UIHelper.create_dialog(parent)

        # Fix dialog's title
        self.__dialog.title(Context.get_text('registry_key_selector'))

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
        self.__create_selection_components()
        self.__create_buttons_components()

        # Reinitialize listbox
        self.__update_ui()

        # Bind closing event
        self.__dialog.protocol("WM_DELETE_WINDOW", self.__on_close)

        # Fix dialog's size and position
        UIHelper.center_dialog(
            dialog=self.__dialog,
            width=800,
            height=450
        )

    def __create_selection_components(self):
        """Create selection components"""

        # Add a label to display the current key
        self.__label_current_key = tk.Label(
            self.__top_frame,
            anchor=tk.W
        )
        self.__label_current_key.pack(
            fill=tk.X,
            padx=Constants.UI_PAD_BIG
        )

        # Add a listbox to display keys
        self.__listbox = tk.Listbox(
            self.__top_frame,
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

        # Bind selection changed
        self.__listbox.bind("<<ListboxSelect>>", self.__on_selection_changed)

    def __create_buttons_components(self):
        """Create buttons components"""

        # Create frame for buttons
        buttons_frame = tk.Frame(self.__bottom_frame)
        buttons_frame.pack(
            side=tk.BOTTOM,
            pady=Constants.UI_PAD_SMALL,
            fill=tk.Y
        )

        # Create buttons to cancel and validate
        button_cancel = tk.Button(
            buttons_frame,
            text=Context.get_text(
                'target_action_cancel',
                target=Context.get_text('target_selection')
            ),
            command=self.__cancel
        )
        button_cancel.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )

        self.__button_validate = tk.Button(
            buttons_frame,
            text=Context.get_text(
                'target_action_validate',
                target=Context.get_text('target_selection')
            ),
            command=self.__validate
        )
        self.__button_validate.config(state=tk.DISABLED)
        self.__button_validate.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )

    def __cancel(self):
        """Cancel"""

        self.__on_close()

    def __validate(self):
        """Validate"""

        # Call back
        self.__callback(
            self.__current_key[1:] + Constants.REGEDIT_KEY_SEPARATOR +
            self.__get_selected_item_name()
        )

        # Close the dialog
        UIHelper.close_dialog(self.__dialog)

    def __on_close(self):
        """Called when closing"""

        # Call back
        self.__callback(None)

        # Close the dialog
        UIHelper.close_dialog(self.__dialog)

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

        # Build context menu
        context_menu = tk.Menu(self.__dialog, tearoff=0)

        # Retrieved selected item's name
        selected_item_name = self.__get_selected_item_name()

        # If sub key
        if selected_item_name is not None and \
                selected_item_name != Context.get_text('registry_key_parent'):
            self.__add_context_menu_command(
                context_menu=context_menu,
                label=Context.get_text(
                    'target_action_open',
                    target=Context.get_text('target_regedit_key')
                ),
                command=self.__open_key
            )

        # Show context menu in the mouse's position
        context_menu.post(event.x_root, event.y_root)

    def __open_key(self):
        """Open a key"""

        self.__on_double_click(None)

    def __on_double_click(self, event):
        """Called when double click on an item"""

        # Retrieved selected item's name
        selected_item_name = self.__get_selected_item_name()

        if selected_item_name == Context.get_text('registry_key_parent'):
            self.__current_key = Constants.REGEDIT_KEY_SEPARATOR.join(
                self.__current_key.split(Constants.REGEDIT_KEY_SEPARATOR)[:-1]
            )
        else:
            self.__current_key += Constants.REGEDIT_KEY_SEPARATOR
            self.__current_key += selected_item_name

        # Update UI
        self.__update_ui()

    def __on_selection_changed(self, event):
        """Called when selection changed"""

        # Retrieved selected item's name
        selected_item_name = self.__get_selected_item_name()

        # Define if validate is enabled or not
        validate_state = tk.DISABLED
        if selected_item_name is not None and \
                selected_item_name != Context.get_text('registry_key_parent'):
            validate_state = tk.NORMAL

        self.__button_validate.config(state=validate_state)

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

    def __retrieve_key_tree(
        self,
        key: str
    ):
        """Retrieve key's tree"""

        result = self.__registry_keys_tree
        for sub_key in key.split(Constants.REGEDIT_KEY_SEPARATOR):
            if len(sub_key) == 0:
                continue
            result = result[sub_key]
        return result

    def __update_ui(
        self
    ):
        """Update UI"""

        # Update current key label
        current_key_path = Constants.REGEDIT_ROOT_KEY_NAME
        if len(self.__current_key) > 0:
            if current_key_path != Constants.REGEDIT_ROOT_KEY_NAME:
                current_key_path += Constants.REGEDIT_KEY_SEPARATOR
            current_key_path += self.__current_key
        self.__label_current_key.config(
            text=Context.get_text(
                'registry_key_current',
                key=current_key_path
            )
        )

        # Remove selection
        self.__listbox.selection_clear(0, tk.END)

        # Reinitialize the listbox
        self.__listbox.delete(0, tk.END)
        self.__listbox.selection_clear(0, tk.END)

        # Retrieve current key's tree
        current_key_tree = self.__retrieve_key_tree(
            key=self.__current_key
        )

        # Show item for parent key
        if len(self.__current_key) > 0:
            self.__listbox.insert(
                tk.END,
                Context.get_text('registry_key_parent')
            )

        # Add sub keys
        for sub_key in current_key_tree:
            self.__listbox.insert(
                tk.END,
                f"📁 {sub_key}"
            )

        self.__on_selection_changed(None)
