#!/usr/bin/python3
"""Dialog to edit media"""

import tkinter as tk
import os
from pathlib import Path
from tkinter import ttk

from libraries.constants.constants import Category, Component, Constants, Media
from libraries.context.context import Context
from libraries.csv.csv_helper import CsvHelper
from libraries.list.list_helper import ListHelper
from libraries.ui.ui_helper import UIHelper
from libraries.ui.ui_media import UIMediaModeConfig, UIMedia
from libraries.ui.ui_table import UITable
from libraries.verifier.verifier import Verifier

# pylint: disable=attribute-defined-outside-init, too-many-locals
# pylint: disable=too-many-instance-attributes, too-many-statements
# pylint: disable=too-many-branches


class MediaEditorDialog:
    """Dialog to edit media"""

    def __init__(
        self,
        parent,
        callback: any
    ):
        """Initialize dialog"""

        self.__callback = callback
        self.__table = None
        self.__current_item_id = None
        self.__current_media_path = None
        self.__current_mode = Context.get_text('media_mode_selecting')
        self.__media_components: list[UIMedia] = []
        self.__media_analysis_checkbox_var = tk.BooleanVar()

        # Create dialog
        self.__dialog = tk.Toplevel(parent)

        # Fix dialog's title
        self.__dialog.title(Context.get_text('edit_media'))

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
        self.__create_category_components()
        self.__create_media_components()
        self.__create_close_components()

        # Bind closing event to stop all media
        self.__dialog.protocol("WM_DELETE_WINDOW", self.__on_close)

        # Select the first mode
        self.__mode_combo.current(0)

        # Select the first row
        self.__table.set_selected_rows([0])

        # Show all media components
        for media_component in self.__media_components:
            media_component.pack(
                side=tk.TOP,
                padx=Constants.UI_PAD_SMALL,
                pady=Constants.UI_PAD_SMALL
            )

    def __create_category_components(self):
        """Create category components"""

        # Create category frames
        category_label_frame = tk.LabelFrame(
            self.__top_frame,
            text=Context.get_text(Context.get_selected_category().value)
        )
        category_label_frame.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=Constants.UI_PAD_BIG,
            pady=Constants.UI_PAD_BIG
        )
        category_actions_frame = tk.Frame(category_label_frame)
        category_actions_frame.pack(
            side=tk.TOP,
            fill=tk.Y
        )
        category_frame = tk.Frame(category_label_frame)
        category_frame.pack(
            side=tk.TOP,
            fill=tk.BOTH,
            expand=True,
            pady=Constants.UI_PAD_SMALL
        )

        # Build rows
        selected_rows = []
        match(Context.get_selected_category()):
            case Category.TABLES:
                selected_rows = Context.get_selected_tables_rows()

            case Category.PLAYLISTS:
                selected_rows = Context.get_selected_playlists_rows()

        rows = []
        for selected_row in selected_rows:
            row = {
                Constants.UI_TABLE_KEY_COL_SELECTION: False,
                Constants.UI_TABLE_KEY_COL_ID: selected_row[Constants.UI_TABLE_KEY_COL_ID],
                Constants.UI_TABLE_KEY_COL_NAME: selected_row[Constants.UI_TABLE_KEY_COL_NAME],
                Component.PINUP_MEDIA.value: selected_row[Component.PINUP_MEDIA.value]
            }

            # Retrieve color
            row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                row=row
            )

            rows.append(row)

        # Create table
        self.__table = UITable(
            parent=category_frame,
            on_selected_rows_change=self.__on_selected_rows_changed,
            rows=rows,
            multiple_selection=False
        )

    def __create_media_components(self):
        """Create media components"""

        # Create media frames
        media_label_frame = tk.LabelFrame(
            self.__top_frame,
            text=Context.get_text('media_title')
        )
        media_label_frame.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            padx=Constants.UI_PAD_BIG,
            pady=Constants.UI_PAD_BIG
        )
        media_actions_frame = tk.Frame(media_label_frame)
        media_actions_frame.pack(
            side=tk.TOP,
            fill=tk.Y
        )
        media_frame = tk.Frame(media_label_frame)
        media_frame.pack(
            side=tk.TOP,
            fill=tk.BOTH
        )
        media_left_frame = tk.Frame(
            media_frame
        )
        media_left_frame.pack(
            side=tk.LEFT
        )
        media_center_frame = tk.Frame(
            media_frame
        )
        media_center_frame.pack(
            side=tk.LEFT
        )
        media_right_frame = tk.Frame(
            media_frame
        )
        media_right_frame.pack(
            side=tk.LEFT
        )

        # Create Combobox for mode
        mode_label = tk.Label(
            media_actions_frame,
            text=Context.get_text('media_mode')
        )
        mode_label.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        modes = []
        match(Context.get_selected_category()):
            case Category.TABLES:
                modes = [
                    Context.get_text('media_mode_selecting'),
                    Context.get_text('media_mode_loading')
                ]

            case Category.PLAYLISTS:
                modes = [
                    Context.get_text('media_mode_selecting')
                ]
        self.__mode_combo = ttk.Combobox(
            media_actions_frame,
            values=modes
        )
        self.__mode_combo.config(state="readonly")
        self.__mode_combo.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.__mode_combo.bind("<<ComboboxSelected>>", self.__on_mode_changed)

        # Create buttons
        self.__button_mute_all_media = tk.Button(
            media_actions_frame,
            text=Context.get_text('media_action_mute'),
            command=self.__mute_all_media_components
        )
        self.__button_mute_all_media.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_BIG,
            pady=Constants.UI_PAD_SMALL
        )
        self.__button_unmute_all_media = tk.Button(
            media_actions_frame,
            text=Context.get_text('media_action_unmute'),
            command=self.__unmute_all_media_components
        )
        self.__button_unmute_all_media.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_BIG,
            pady=Constants.UI_PAD_SMALL
        )

        # Create checkboxes
        frame_media_analysis = tk.Frame(media_actions_frame)
        frame_media_analysis.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_BIG,
            pady=Constants.UI_PAD_SMALL
        )
        checkbox_media_analysis = tk.Checkbutton(
            frame_media_analysis,
            variable=self.__media_analysis_checkbox_var
        )
        checkbox_media_analysis.pack(
            side=tk.LEFT
        )
        label_media_analysis = tk.Label(
            frame_media_analysis,
            text=Context.get_text('media_analysis')
        )
        label_media_analysis.pack(
            side=tk.LEFT
        )
        label_media_analysis.bind(
            "<Button-1>",
            lambda e: checkbox_media_analysis.invoke()
        )

        # Append media for AUDIO
        current_media = Media.AUDIO
        current_selecting_folder = 'Audio'
        current_loading_folder = 'AudioLaunch'
        if current_media.value in Context.list_available_media():
            name_suffix = None
            screen_number = Context.get_screen_number_by_media()[
                current_media.value]
            if screen_number >= 0:
                current_loading_folder = 'Loading'
                name_suffix = f'01(SCREEN{screen_number})'
            media_component = UIMedia(
                update_media_actions=self.__update_media_actions,
                parent=media_left_frame,
                title=Context.get_text(current_media.value),
                modes_configs=[
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_selecting'),
                        folder=current_selecting_folder
                    ),
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_loading'),
                        folder=current_loading_folder,
                        name_suffix=name_suffix
                    )
                ],
                width=100,
                height=100
            )
            self.__media_components.append(media_component)

        # Append media for DMD
        current_media = Media.DMD
        current_selecting_folder = 'DMD'
        current_loading_folder = 'DMD'
        if current_media.value in Context.list_available_media():
            name_suffix = None
            screen_number = Context.get_screen_number_by_media()[
                current_media.value]
            if screen_number >= 0:
                current_loading_folder = 'Loading'
                name_suffix = f'01(SCREEN{screen_number})'
            media_component = UIMedia(
                update_media_actions=self.__update_media_actions,
                parent=media_left_frame,
                title=Context.get_text(current_media.value),
                modes_configs=[
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_selecting'),
                        folder=current_selecting_folder
                    ),
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_loading'),
                        folder=current_loading_folder,
                        name_suffix=name_suffix
                    )
                ],
                width=100,
                height=100
            )
            self.__media_components.append(media_component)

        # Append media for FLYER
        current_media = Media.FLYER
        current_selecting_folder = 'GameInfo'
        current_loading_folder = 'GameInfo'
        if current_media.value in Context.list_available_media():
            name_suffix = None
            screen_number = Context.get_screen_number_by_media()[
                current_media.value]
            if screen_number >= 0:
                current_loading_folder = 'Loading'
                name_suffix = f'01(SCREEN{screen_number})'
            media_component = UIMedia(
                update_media_actions=self.__update_media_actions,
                parent=media_left_frame,
                title=Context.get_text(current_media.value),
                modes_configs=[
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_selecting'),
                        folder=current_selecting_folder
                    ),
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_loading'),
                        folder=current_loading_folder,
                        name_suffix=name_suffix
                    )
                ],
                width=100,
                height=100
            )
            self.__media_components.append(media_component)

        # Append media for HELP
        current_media = Media.HELP
        current_selecting_folder = 'GameHelp'
        current_loading_folder = 'GameHelp'
        if current_media.value in Context.list_available_media():
            name_suffix = None
            screen_number = Context.get_screen_number_by_media()[
                current_media.value]
            if screen_number >= 0:
                current_loading_folder = 'Loading'
                name_suffix = f'01(SCREEN{screen_number})'
            media_component = UIMedia(
                update_media_actions=self.__update_media_actions,
                parent=media_left_frame,
                title=Context.get_text(current_media.value),
                modes_configs=[
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_selecting'),
                        folder=current_selecting_folder
                    ),
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_loading'),
                        folder=current_loading_folder,
                        name_suffix=name_suffix
                    )
                ],
                width=100,
                height=100
            )
            self.__media_components.append(media_component)

        # Append media for TOPPER
        current_media = Media.TOPPER
        current_selecting_folder = 'Topper'
        current_loading_folder = 'Topper'
        if current_media.value in Context.list_available_media():
            name_suffix = None
            screen_number = Context.get_screen_number_by_media()[
                current_media.value]
            if screen_number >= 0:
                current_loading_folder = 'Loading'
                name_suffix = f'01(SCREEN{screen_number})'
            media_component = UIMedia(
                update_media_actions=self.__update_media_actions,
                parent=media_center_frame,
                title=Context.get_text(current_media.value),
                modes_configs=[
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_selecting'),
                        folder=current_selecting_folder
                    ),
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_loading'),
                        folder=current_loading_folder,
                        name_suffix=name_suffix
                    )
                ],
                width=288,
                height=50
            )
            self.__media_components.append(media_component)

        # Append media for BACKGLASS
        current_media = Media.BACKGLASS
        current_selecting_folder = 'BackGlass'
        current_loading_folder = 'BackGlass'
        if current_media.value in Context.list_available_media():
            name_suffix = None
            screen_number = Context.get_screen_number_by_media()[
                current_media.value]
            if screen_number >= 0:
                current_loading_folder = 'Loading'
                name_suffix = f'01(SCREEN{screen_number})'
            media_component = UIMedia(
                update_media_actions=self.__update_media_actions,
                parent=media_center_frame,
                title=Context.get_text(current_media.value),
                modes_configs=[
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_selecting'),
                        folder=current_selecting_folder
                    ),
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_loading'),
                        folder=current_loading_folder,
                        name_suffix=name_suffix
                    )
                ],
                width=288,
                height=162
            )
            self.__media_components.append(media_component)

        # Append media for FULL_DMD
        current_media = Media.FULL_DMD
        current_selecting_folder = 'Menu'
        current_loading_folder = 'Menu'
        if current_media.value in Context.list_available_media():
            name_suffix = None
            screen_number = Context.get_screen_number_by_media()[
                current_media.value]
            if screen_number >= 0:
                current_loading_folder = 'Loading'
                name_suffix = f'01(SCREEN{screen_number})'
            media_component = UIMedia(
                update_media_actions=self.__update_media_actions,
                parent=media_center_frame,
                title=Context.get_text(current_media.value),
                modes_configs=[
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_selecting'),
                        folder=current_selecting_folder
                    ),
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_loading'),
                        folder=current_loading_folder,
                        name_suffix=name_suffix
                    )
                ],
                width=192,
                height=108
            )
            self.__media_components.append(media_component)

        # Append media for PLAYFIELD
        current_media = Media.PLAYFIELD
        current_selecting_folder = 'PLAYFIELD'
        current_loading_folder = 'PLAYFIELD'
        if current_media.value in Context.list_available_media():
            name_suffix = None
            screen_number = Context.get_screen_number_by_media()[
                current_media.value]
            if screen_number >= 0:
                current_loading_folder = 'Loading'
                name_suffix = f'01(SCREEN{screen_number})'
            media_component = UIMedia(
                update_media_actions=self.__update_media_actions,
                parent=media_center_frame,
                title=Context.get_text(current_media.value),
                modes_configs=[
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_selecting'),
                        folder=current_selecting_folder
                    ),
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_loading'),
                        folder=current_loading_folder,
                        name_suffix=name_suffix
                    )
                ],
                width=216,
                height=384,
                rotate=90
            )
            self.__media_components.append(media_component)

        # Append media for WHEEL_BAR
        current_media = Media.WHEEL_BAR
        current_selecting_folder = 'GameSelect'
        current_loading_folder = 'GameSelect'
        if current_media.value in Context.list_available_media() and \
                Context.get_selected_category() == Category.PLAYLISTS:
            name_suffix = None
            screen_number = Context.get_screen_number_by_media()[
                current_media.value]
            if screen_number >= 0:
                current_loading_folder = 'Loading'
                name_suffix = f'01(SCREEN{screen_number})'
            media_component = UIMedia(
                update_media_actions=self.__update_media_actions,
                parent=media_right_frame,
                title=Context.get_text(current_media.value),
                modes_configs=[
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_selecting'),
                        folder=current_selecting_folder
                    ),
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_loading'),
                        folder=current_loading_folder,
                        name_suffix=name_suffix
                    )
                ],
                width=100,
                height=100
            )
            self.__media_components.append(media_component)

        # Append media for WHEEL_IMAGE
        current_media = Media.WHEEL_IMAGE
        current_selecting_folder = 'Wheel'
        current_loading_folder = 'Wheel'
        if current_media.value in Context.list_available_media():
            name_suffix = None
            screen_number = Context.get_screen_number_by_media()[
                current_media.value]
            if screen_number >= 0:
                current_loading_folder = 'Loading'
                name_suffix = f'01(SCREEN{screen_number})'
            media_component = UIMedia(
                update_media_actions=self.__update_media_actions,
                parent=media_right_frame,
                title=Context.get_text(current_media.value),
                modes_configs=[
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_selecting'),
                        folder=current_selecting_folder
                    ),
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_loading'),
                        folder=current_loading_folder,
                        name_suffix=name_suffix
                    )
                ],
                width=100,
                height=100
            )
            self.__media_components.append(media_component)

        # Append media for OTHER
        current_media = Media.OTHER
        current_selecting_folder = 'Other'
        current_loading_folder = 'Other'
        if current_media.value in Context.list_available_media():
            name_suffix = None
            screen_number = Context.get_screen_number_by_media()[
                current_media.value]
            if screen_number >= 0:
                current_loading_folder = 'Loading'
                name_suffix = f'01(SCREEN{screen_number})'
            media_component = UIMedia(
                update_media_actions=self.__update_media_actions,
                parent=media_right_frame,
                title=Context.get_text(current_media.value),
                modes_configs=[
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_selecting'),
                        folder=current_selecting_folder
                    ),
                    UIMediaModeConfig(
                        mode=Context.get_text('media_mode_loading'),
                        folder=current_loading_folder,
                        name_suffix=name_suffix
                    )
                ],
                width=100,
                height=100
            )
            self.__media_components.append(media_component)

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

    def __on_close(self):
        """Called when closing"""

        # Stop all media components
        for media_component in self.__media_components:
            media_component.stop_media()

        # Call back
        self.__callback()

        # Close the dialog
        UIHelper.close_dialog(self.__dialog)

    def __on_selected_rows_changed(self):
        """Called when selected rows changed"""

        # Retrieve selected rows
        selected_rows = self.__table.get_selected_rows()

        # Do nothing if no selected row
        if len(selected_rows) != 1:
            return

        # Retrieve info from selected item
        item_id = selected_rows[0][Constants.UI_TABLE_KEY_COL_ID]
        csv_item = ListHelper.select_item(
            item_id=item_id,
            a_list=CsvHelper.read_data(
                file_path=Context.get_csv_path()
            ),
            id_column=Constants.CSV_COL_ID
        )
        item_version = csv_item.get(
            Constants.CSV_COL_VERSION,
            Constants.LATEST_PATH
        )

        # Retrieve the media path
        match(Context.get_selected_category()):
            case Category.TABLES:
                media_path = Path(os.path.join(
                    Context.get_working_path(),
                    'tables',
                    Context.get_selected_emulator().value,
                    item_id,
                    item_version,
                    'media'
                ))

            case Category.PLAYLISTS:
                media_path = Path(os.path.join(
                    Context.get_working_path(),
                    'playlists',
                    item_id,
                    item_version,
                    'media'
                ))

        # Change current item's id
        self.__current_item_id = item_id

        # Change current media's path
        self.__current_media_path = media_path

        # Update all media components
        self.__update_all_media_components()

    def __on_mode_changed(self, event):
        """Called when a mode changed"""

        # Change current mode
        self.__current_mode = event.widget.get()

        self.__table.focus()

        # Update all media components
        self.__update_all_media_components()

    def __update_all_media_components(self):
        """Update all media components"""

        # Do nothing if missing current media's path
        if self.__current_media_path is None:
            return

        # Do nothing if missing current mode
        if self.__current_mode is None:
            return

        # Update all media
        for media_component in self.__media_components:
            media_component.update_media(
                item_id=self.__current_item_id,
                media_path=self.__current_media_path,
                mode=self.__current_mode,
                analysis_enabled=self.__media_analysis_checkbox_var.get()
            )

    def __update_media_actions(self):
        """Update media actions"""

        # Update buttons to mute/unmute media
        muted_components_count = 0
        unmuted_components_count = 0
        for media_component in self.__media_components:
            if media_component.is_muted():
                muted_components_count += 1
            else:
                unmuted_components_count += 1

        if unmuted_components_count > 0:
            self.__button_mute_all_media.config(
                state=tk.NORMAL
            )
        else:
            self.__button_mute_all_media.config(
                state=tk.DISABLED
            )

        if muted_components_count > 0:
            self.__button_unmute_all_media.config(
                state=tk.NORMAL
            )
        else:
            self.__button_unmute_all_media.config(
                state=tk.DISABLED
            )

    def __mute_all_media_components(self):
        """Mute all media components"""

        # Mute all media
        for media_component in self.__media_components:
            # Mute component if not already muted
            if not media_component.is_muted():
                media_component.toggle_mute_unmute()

    def __unmute_all_media_components(self):
        """Unmute all media components"""

        # Unmute all media
        for media_component in self.__media_components:
            # Unmute component if not already muted
            if media_component.is_muted():
                media_component.toggle_mute_unmute()
