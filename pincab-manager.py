
# pylint: disable=invalid-name
#!/usr/bin/python3
"""Application to manage my Pincab"""

import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from dialogs.about.about_dialog import AboutDialog
from dialogs.editor.media_editor_dialog import MediaEditorDialog
from dialogs.editor.playlists_editor_dialog import PlaylistsEditorDialog
from dialogs.editor.tables_editor_dialog import TablesEditorDialog
from dialogs.refresh.refresh_dialog import RefreshDialog
from dialogs.setup.setup_dialog import SetupDialog
from dialogs.execute.execute_dialog import ExecuteDialog
from libraries.csv.csv_helper import CsvHelper
from libraries.constants.constants import Action, Category, Component, Constants, Emulator
from libraries.context.context import Context
from libraries.ui.ui_helper import UIHelper
from libraries.ui.ui_table import UITable

# pylint: disable=attribute-defined-outside-init
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-locals
# pylint: disable=too-many-lines


class ApplicationWindow:
    """Application to manage Pincab"""

    def __on_selected_rows_changed(self):
        """Called when selected rows changed"""

        # Retrieve selected rows
        selected_top_rows = self.table_top.get_selected_rows()
        selected_bottom_rows = self.table_bottom.get_selected_rows()

        # Update execute button state
        if len(selected_top_rows) > 0 and len(selected_bottom_rows) > 0:
            self.button_execute.config(state=tk.NORMAL)
        else:
            # Authorize edit if no rows in top
            if len(selected_bottom_rows) > 0 and Context.get_selected_action() in [
                Action.EDIT
            ]:
                self.button_execute.config(state=tk.NORMAL)
            else:
                self.button_execute.config(state=tk.DISABLED)

    def __on_combo_changed(self, event):
        """Called when a combo changed"""

        # Update context from selection
        Context.set_selected_category(
            list(Category)[self.combo_category.current()]
        )

        emulator_idx = self.combo_emulator.current()
        emulator_idx = max(emulator_idx, 0)

        if len(Context.list_available_emulators()) <= emulator_idx:
            return

        for emulator in Emulator:
            if emulator.value == Context.list_available_emulators()[emulator_idx]:
                Context.set_selected_emulator(emulator)

        Context.set_selected_action(
            list(Action)[self.combo_action.current()]
        )

        # If source is category, show/hide emulator and select first action
        if event.widget == self.combo_category:
            # Show/Hide combo emulator depending on selected category
            if Context.get_selected_category() == Category.TABLES:
                self.label_emulator.pack(
                    side=tk.LEFT,
                    padx=Constants.UI_PAD_SMALL
                )
                self.combo_emulator.pack(
                    side=tk.LEFT,
                    padx=Constants.UI_PAD_SMALL
                )
                self.combo_emulator.current(0)
            else:
                self.label_emulator.pack_forget()
                self.combo_emulator.pack_forget()

            # Update actions depending on selected category
            category_actions = []
            for action in Action:
                if action == Action.COPY and \
                        Context.get_selected_category() != Category.TABLES and \
                        Context.get_selected_category() != Category.PLAYLISTS:
                    continue
                if action == Action.EDIT and \
                        Context.get_selected_category() != Category.TABLES and \
                        Context.get_selected_category() != Category.PLAYLISTS:
                    continue
                category_actions.append(Context.get_text(
                    action.value,
                    category=Context.get_text(
                        Context.get_selected_category().value
                    )
                ))
            self.combo_action.configure(
                values=category_actions
            )

            self.combo_action.current(0)
            self.combo_action.event_generate("<<ComboboxSelected>>")
            return

        # Update data
        self.__update_data()

    def __update_data(self):
        """Update data"""

        # Force refresh if auto refresh or no CSV exists with data
        if Context.is_auto_refresh() or (
            Context.get_setup_file_path().exists() and
            not Context.get_selected_rows_csv_path().exists()
        ):
            # If auto refresh
            self.__load_refresh()
        else:
            # Update data
            self.__update_ui()

    def __update_ui(self):
        """Update UI depending on choices made in combos"""

        # Create table top from CSV
        table_top_rows = []
        for row in CsvHelper.read_data(
            file_path=Context.get_selected_rows_csv_path()
        ):
            table_top_row = {}
            for key, value in row.items():
                if value == Constants.CSV_YES_VALUE:
                    table_top_row[key] = True
                elif value == Constants.CSV_NO_VALUE:
                    table_top_row[key] = False
                else:
                    table_top_row[key] = value
            table_top_rows.append(table_top_row)

        self.__create_table_top(
            rows=table_top_rows
        )

        # Change labels for top frame
        self.table_top_frame.config(text=self.combo_category.get())

        # Create table bottom
        components = []
        match(Context.get_selected_category()):
            case Category.TABLES:
                components.append(Component.EMULATOR_TABLE)
                components.append(Component.PINUP_MEDIA)
                if Context.get_selected_action() != Action.EDIT:
                    components.append(Component.PINUP_VIDEOS)
                    if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:
                        components.append(Component.CONFIG_XML)
                        components.append(Component.CONFIG_REG)

            case Category.PLAYLISTS:
                components.append(Component.EMULATOR_PLAYLIST)
                components.append(Component.PINUP_MEDIA)

            case Category.BDD_TABLES:
                components.append(Component.PINUP_DATABASE)

            case Category.CONFIGS_FILES:
                components.append(Component.SYSTEM_32_BITS)
                components.append(Component.SYSTEM_64_BITS)

        table_bottom_rows = []
        for component in components:
            table_bottom_rows.append({
                Constants.UI_TABLE_KEY_COL_SELECTION: False,
                Constants.UI_TABLE_KEY_COL_ID: Context.get_text(component.value),
                Constants.UI_TABLE_KEY_COL_NAME: Context.get_text(component.value),
                Constants.UI_TABLE_KEY_COLOR: Constants.ITEM_COLOR_BLACK
            })

        self.__create_table_bottom(
            rows=table_bottom_rows
        )

        # Update button state
        self.button_execute.config(state=tk.DISABLED)

        # Initialize context
        Context.set_selected_tables_rows([])
        Context.set_selected_playlists_rows([])
        Context.set_selected_configs_rows([])
        Context.set_selected_components([])

    def __load_refresh(self):
        """Load refresh"""

        # Load dialog to refresh
        RefreshDialog(
            self.__window,
            callback=self.__update_ui
        )

    def __load_setup(self):
        """Load setup"""

        # Load dialog to setup
        SetupDialog(
            self.__window,
            callback=self.__update_components_from_context
        )

    def __load_about(self):
        """Load about"""

        # Load dialog for about
        AboutDialog(
            self.__window
        )

    def __execute(self):
        """Execute"""

        # Update context
        match(Context.get_selected_category()):
            case Category.TABLES:
                Context.set_selected_tables_rows(
                    self.table_top.get_selected_rows()
                )
                Context.set_selected_components(
                    self.table_bottom.get_selected_rows()
                )

            case Category.PLAYLISTS:
                Context.set_selected_playlists_rows(
                    self.table_top.get_selected_rows()
                )
                Context.set_selected_components(
                    self.table_bottom.get_selected_rows()
                )

            case Category.BDD_TABLES:
                Context.set_selected_bdd_tables_rows(
                    self.table_top.get_selected_rows()
                )
                Context.set_selected_components(
                    self.table_bottom.get_selected_rows()
                )

            case Category.CONFIGS_FILES:
                Context.set_selected_configs_rows(
                    self.table_top.get_selected_rows()
                )
                Context.set_selected_components(
                    self.table_bottom.get_selected_rows()
                )

        if Context.get_selected_action() == Action.COPY:
            # If action is COPY, ask to select a folder
            folder_path = filedialog.askdirectory(
                parent=self.__window
            )

            # Cancel execution if no folder selected
            if not folder_path:
                return

            # Update selected folder's path
            Context.set_selected_folder_path(
                folder_path=folder_path
            )

        if Context.get_selected_action() == Action.EDIT:

            selected_component = Context.get_selected_components()[0]
            match(selected_component):
                case Component.PINUP_MEDIA:
                    # If component PINUP_MEDIA
                    MediaEditorDialog(
                        self.__window,
                        callback=self.__update_data
                    )

                case Component.EMULATOR_TABLE:
                    # If component EMULATOR_TABLE
                    TablesEditorDialog(
                        self.__window,
                        callback=self.__update_data
                    )

                case Component.EMULATOR_PLAYLIST:
                    # If component EMULATOR_PLAYLIST
                    PlaylistsEditorDialog(
                        self.__window,
                        callback=self.__update_data
                    )
        else:
            # If other action, execution is automatic
            ExecuteDialog(
                self.__window,
                callback=self.__update_data
            )

    def __create_top_components(self):
        """Create top components"""

        # Create top frame
        top_frame = tk.Frame(self.__window)
        top_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            pady=Constants.UI_PAD_BIG
        )

        # Create combo frame
        combo_frame = tk.Frame(top_frame)
        combo_frame.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True
        )

        # Create Combobox for category
        self.label_category = tk.Label(
            combo_frame
        )
        self.label_category.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.combo_category = ttk.Combobox(
            combo_frame
        )
        self.combo_category.config(state="readonly")
        self.combo_category.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.combo_category.bind(
            "<<ComboboxSelected>>",
            self.__on_combo_changed
        )

        # Create Combobox for action
        self.label_action = tk.Label(
            combo_frame
        )
        self.label_action.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.combo_action = ttk.Combobox(
            combo_frame,
            width=35
        )
        self.combo_action.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.combo_action.config(state="readonly")
        self.combo_action.bind(
            "<<ComboboxSelected>>",
            self.__on_combo_changed
        )

        # Create Combobox for emulator
        self.label_emulator = tk.Label(
            combo_frame
        )
        self.label_emulator.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.combo_emulator = ttk.Combobox(
            combo_frame,
            values=Context.list_available_emulators()
        )
        self.combo_emulator.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.combo_emulator.config(state="readonly")
        self.combo_emulator.bind(
            "<<ComboboxSelected>>",
            self.__on_combo_changed
        )

        # Create setup/about frame
        setup_about_frame = tk.Frame(top_frame)
        setup_about_frame.pack(
            side=tk.RIGHT,
            padx=Constants.UI_PAD_BIG
        )

        # Button to setup
        self.button_setup = tk.Button(
            setup_about_frame,
            command=self.__load_setup
        )
        self.button_setup.pack(
            side=tk.TOP,
            fill=tk.X,
            expand=True,
            pady=(0, Constants.UI_PAD_SMALL)
        )

        # Button for about
        self.button_about = tk.Button(
            setup_about_frame,
            command=self.__load_about
        )
        self.button_about.pack(
            side=tk.BOTTOM,
            fill=tk.X,
            expand=True,
            pady=(Constants.UI_PAD_SMALL, 0)
        )

        # Button to refresh
        self.button_refresh = tk.Button(
            top_frame,
            command=self.__load_refresh
        )
        self.button_refresh.pack(
            side=tk.RIGHT,
            padx=Constants.UI_PAD_SMALL
        )

    def __create_center_components(self):
        """Create center components"""
        self.center_frame = tk.Frame(self.__window)
        self.center_frame.pack(
            side=tk.TOP,
            fill=tk.BOTH,
            expand=True,
        )

        self.__create_table_top_frame()
        self.__create_table_bottom_frame()

    def __create_table_top(
        self,
        rows: list
    ):
        """Create the table top"""

        # Clear the frame
        UIHelper.clear_frame(self.table_top_frame)

        # Create the table
        self.table_top = UITable(
            parent=self.table_top_frame,
            on_selected_rows_change=self.__on_selected_rows_changed,
            rows=rows
        )

    def __create_table_bottom(
        self,
        rows: list
    ):
        """Create the table bottom"""

        # Clear the frame
        UIHelper.clear_frame(self.table_bottom_frame)

        # Define if multiple selection
        multiple_selection = True
        if Context.get_selected_action() == Action.EDIT:
            multiple_selection = False

        # Create the table
        self.table_bottom = UITable(
            parent=self.table_bottom_frame,
            on_selected_rows_change=self.__on_selected_rows_changed,
            rows=rows,
            multiple_selection=multiple_selection
        )

    def __create_table_top_frame(self):
        """Create frame for table top"""

        # Create frame
        self.table_top_frame = tk.LabelFrame(
            self.center_frame,
            text=''
        )
        self.table_top_frame.pack(
            side=tk.TOP,
            fill=tk.BOTH,
            expand=True,
            padx=Constants.UI_PAD_BIG
        )

    def __create_table_bottom_frame(self):
        """Create frame for table bottom"""

        # Create frame
        self.table_bottom_frame = tk.LabelFrame(
            self.center_frame,
            text=''
        )
        self.table_bottom_frame.pack(
            side=tk.TOP,
            fill=tk.BOTH,
            expand=True,
            padx=Constants.UI_PAD_BIG,
            pady=Constants.UI_PAD_BIG
        )

    def __create_bottom_components(self):
        """Create bottom components"""

        # Create bottom frame
        bottom_frame = tk.Frame(self.__window)
        bottom_frame.pack(
            side=tk.BOTTOM,
            fill=tk.X,
            pady=Constants.UI_PAD_BIG
        )

        # Create button to execute
        self.button_execute = tk.Button(
            bottom_frame,
            command=self.__execute
        )
        self.button_execute.config(state=tk.DISABLED)
        self.button_execute.pack(
            side=tk.BOTTOM
        )

    def __update_components_from_context(self):
        """Update components from context"""

        # Fix windows's title
        title = Context.get_text('title')
        title += f' ({Context.get_app_version()})'
        if Context.is_simulated():
            title += f' {Context.get_text("simulated")}'
        self.__window.title(title)

        # Fix frames text
        self.table_bottom_frame.config(
            text=Context.get_text('components')
        )

        # Fix buttons text
        self.button_setup.config(
            text=Context.get_text('setup')
        )
        self.button_about.config(
            text=Context.get_text('about')
        )
        self.button_refresh.config(
            text=Context.get_text('refresh')
        )
        self.button_execute.config(
            text=Context.get_text('execute')
        )

        # Fix labels text
        self.label_category.config(
            text=Context.get_text('category')
        )
        self.label_emulator.config(
            text=Context.get_text('emulator')
        )
        self.label_action.config(
            text=Context.get_text('action')
        )

        # Fix combobox text
        self.combo_category.config(
            values=[Context.get_text(category.value) for category in Category]
        )

        # Fix values for combobox Emulator
        self.combo_emulator.config(
            values=Context.list_available_emulators()
        )

        # Show combobox emulator
        self.label_emulator.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.combo_emulator.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )

        # Set default selection
        self.combo_category.set('')
        self.combo_emulator.set('')
        self.combo_action.set('')
        self.combo_category.current(0)
        self.combo_category.event_generate("<<ComboboxSelected>>")

        # Fix windows's size and position
        UIHelper.center_window(
            window=self.__window,
            width=1024,
            height=768
        )

    def show(self):
        """Show UI"""

        # Create window
        self.__window = tk.Tk()

        # Handle window close event
        self.__window.protocol("WM_DELETE_WINDOW", self.__on_close)

        # Fix windows's icon
        self.__icon_image = tk.PhotoImage(
            file=os.path.join(
                Context.get_base_path(),
                Constants.RESOURCES_PATH,
                'img',
                'pincab_manager.png'
            )
        )
        self.__window.iconphoto(
            True,
            self.__icon_image
        )

        # Create components
        self.__create_top_components()
        self.__create_center_components()
        self.__create_bottom_components()

        # Update texts
        self.__update_components_from_context()

        # If no setup, load setup
        if not Context.get_setup_file_path().exists():
            self.__load_setup()

        # Show window
        self.__window.mainloop()

    def __on_close(self):
        """Called when the window is closing"""
        Context.destroy()
        self.__window.destroy()


if __name__ == "__main__":
    # python3 pincab-manager.py
    app = ApplicationWindow()
    app.show()
