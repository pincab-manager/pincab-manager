#!/usr/bin/python3
"""Dialog to refresh the application"""

import os
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time

from libraries.bdd.bdd_helper import BddHelper
from libraries.constants.constants import Action, Category, Component, Constants, Emulator
from libraries.context.context import Context
from libraries.csv.csv_helper import CsvHelper
from libraries.file.file_helper import FileHelper
from libraries.list.list_helper import ListHelper
from libraries.ui.ui_helper import UIHelper
from libraries.verifier.verifier import Verifier

# pylint: disable=attribute-defined-outside-init, too-many-branches
# pylint: disable=too-many-instance-attributes, too-many-statements
# pylint: disable=line-too-long, too-many-locals, too-many-lines
# pylint: disable=too-many-return-statements


class RefreshDialog:
    """Dialog to refresh the application"""

    def __init__(
        self,
        parent,
        only_ids: list[str],
        callback: any
    ):
        """Initialize dialog"""

        self.__refresh_done = False
        self.__interruption_requested = False
        self.__only_ids = only_ids
        self.__callback = callback

        # Create dialog
        self.dialog = tk.Toplevel(parent)

        # Fix dialog's title
        self.dialog.title(Context.get_text(
            'refresh',
            target=Context.get_text(
                Context.get_selected_category().value
            )
        ))

        # Fix dialog's size and position
        UIHelper.center_dialog(
            dialog=self.dialog,
            width=480,
            height=75
        )

        # Add a progress bar
        self.progress_bar = ttk.Progressbar(
            self.dialog,
            orient=tk.HORIZONTAL,
            length=500,
            mode='determinate'
        )
        self.progress_bar.pack(
            side=tk.TOP,
            padx=Constants.UI_PAD_BIG,
            pady=Constants.UI_PAD_BIG
        )

        self.progress_label = tk.Label(
            self.dialog
        )
        self.progress_label.pack(
            side=tk.TOP
        )

        # Avoid to close the dialog
        self.dialog.protocol("WM_DELETE_WINDOW", self.__on_close)

        # Execute refresh in a thread
        execution_thread = threading.Thread(
            target=self.__refresh
        )
        execution_thread.start()

    def __refresh(self):
        """Refresh"""

        # Create rows for table top
        table_top_rows = []
        match(Context.get_selected_category()):
            case Category.TABLES:
                # Append row for each table
                csv_tables = CsvHelper.read_data(
                    file_path=Context.get_csv_path()
                )
                bdd_tables = BddHelper.list_tables(
                    bdd_file_path=Context.get_pinup_bdd_path(),
                    emulator=Context.get_selected_emulator()
                )

                match(Context.get_selected_action()):
                    case Action.INSTALL:

                        # Initialize progress bar
                        item_current_counter = 0
                        item_total_counter = self.__count_items_to_refresh(
                            items=csv_tables
                        )
                        self.progress_bar.config(
                            maximum=item_total_counter
                        )

                        # Retrieve tables from CSV
                        for csv_table in csv_tables:
                            csv_table_id = csv_table[Constants.CSV_COL_ID]
                            csv_table_name = csv_table[Constants.CSV_COL_NAME]

                            # Ignore item to refresh if requested
                            if not self.__is_item_to_refresh(csv_table_id):
                                continue

                            # Interrupt process if requested
                            if self.__interruption_requested:
                                self.__on_close()
                                return

                            # Increment progress bar
                            item_current_counter += 1
                            self.progress_bar['value'] = item_current_counter
                            self.progress_label.config(
                                text=Context.get_text(
                                    'refresh_in_progress',
                                    item_name=csv_table_name,
                                    item_current_counter=item_current_counter,
                                    item_total_counter=item_total_counter
                                )
                            )

                            # Waiting 0.1 seconde to see the dialog if the process is quick
                            time.sleep(0.1)

                            # Retrieve CSV table's data
                            csv_table_version = csv_table[Constants.CSV_COL_VERSION]
                            csv_table_rom = csv_table[Constants.CSV_COL_ROM]
                            csv_table_videos_path = csv_table[Constants.CSV_COL_VIDEOS_PATH]

                            # Retrieve BDD Table
                            bdd_table = ListHelper.select_item(
                                item_id=csv_table_id,
                                a_list=bdd_tables,
                                id_column=Constants.BDD_COL_TABLE_ID
                            )

                            # Retrieve BDD table's data
                            bdd_table_id = bdd_table.get(
                                Constants.BDD_COL_TABLE_ID,
                                None
                            )
                            bdd_table_version = bdd_table.get(
                                Constants.BDD_COL_TABLE_VERSION,
                                None
                            )

                            # Build row
                            row = {}
                            row[Constants.UI_TABLE_KEY_COL_SELECTION] = False
                            row[Constants.UI_TABLE_KEY_COL_ID] = csv_table_id
                            row[Constants.UI_TABLE_KEY_COL_NAME] = csv_table_name
                            row[Constants.UI_TABLE_KEY_COL_LATEST_VERSION] = Verifier.verify_csv_bdd_version(
                                csv_version=csv_table_version,
                                bdd_version=bdd_table_version
                            )
                            if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:
                                row[Component.EMULATOR_TABLE.value] = Verifier.verify_table_emulator_install(
                                    bdd_table_id=bdd_table_id,
                                    bdd_table_version=bdd_table_version
                                )
                            else:
                                row[Component.EMULATOR_TABLE.value] = row[Constants.UI_TABLE_KEY_COL_LATEST_VERSION]

                            row[Component.PINUP_MEDIA.value] = Verifier.verify_table_pinup_media_install(
                                bdd_table_id=bdd_table_id,
                                bdd_table_version=bdd_table_version
                            )
                            row[Component.PINUP_VIDEOS.value] = Verifier.verify_table_pinup_videos_install(
                                csv_table_videos_path=csv_table_videos_path,
                                bdd_table_id=bdd_table_id,
                                bdd_table_version=bdd_table_version
                            )
                            if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:
                                row[Component.CONFIG_XML.value] = Verifier.verify_table_xml_config_install(
                                    csv_table_id=csv_table_id,
                                    csv_table_version=csv_table_version,
                                    csv_table_rom=csv_table_rom
                                )
                                row[Component.CONFIG_REG.value] = Verifier.verify_table_reg_config_install(
                                    csv_table_id=csv_table_id,
                                    csv_table_version=csv_table_version,
                                    csv_table_rom=csv_table_rom
                                )

                            # Retrieve color
                            row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                                row=row
                            )

                            # Append row
                            table_top_rows.append(row)

                    case Action.UNINSTALL:

                        # Initialize progress bar
                        item_current_counter = 0
                        item_total_counter = self.__count_items_to_refresh(
                            items=bdd_tables
                        )
                        self.progress_bar.config(
                            maximum=item_total_counter
                        )

                        # Retrieve tables from BDD
                        for bdd_table in bdd_tables:
                            bdd_table_id = bdd_table[Constants.BDD_COL_TABLE_ID]
                            bdd_table_name = bdd_table[Constants.BDD_COL_TABLE_NAME]

                            # Ignore item to refresh if requested
                            if not self.__is_item_to_refresh(bdd_table_id):
                                continue

                            # Interrupt process if requested
                            if self.__interruption_requested:
                                self.__on_close()
                                return

                            # Increment progress bar
                            item_current_counter += 1
                            self.progress_bar['value'] = item_current_counter
                            self.progress_label.config(
                                text=Context.get_text(
                                    'refresh_in_progress',
                                    item_name=bdd_table_name,
                                    item_current_counter=item_current_counter,
                                    item_total_counter=item_total_counter
                                )
                            )

                            # Waiting 0.1 seconde to see the dialog if the process is quick
                            time.sleep(0.1)

                            # Retrieve BDD table's data
                            bdd_table_version = bdd_table[Constants.BDD_COL_TABLE_VERSION]
                            bdd_table_rom = bdd_table[Constants.BDD_COL_TABLE_ROM]

                            if Verifier.verify_none_value(bdd_table_version):
                                bdd_table_version = 'latest'

                            # Retrieve CSV Table
                            csv_table = ListHelper.select_item(
                                item_id=bdd_table_id,
                                a_list=csv_tables,
                                id_column=Constants.CSV_COL_ID
                            )

                            # Retrieve CSV table's data
                            csv_table_version = csv_table.get(
                                Constants.CSV_COL_VERSION,
                                None
                            )
                            csv_table_videos_path = csv_table.get(
                                Constants.CSV_COL_VIDEOS_PATH,
                                None
                            )

                            # Build row
                            row = {}
                            row[Constants.UI_TABLE_KEY_COL_SELECTION] = False
                            row[Constants.UI_TABLE_KEY_COL_ID] = bdd_table_id
                            row[Constants.UI_TABLE_KEY_COL_NAME] = bdd_table_name
                            if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:
                                row[Component.EMULATOR_TABLE.value] = Verifier.verify_table_emulator_uninstall(
                                    bdd_table_id=bdd_table_id,
                                    bdd_table_version=bdd_table_version
                                )
                            else:
                                row[Component.EMULATOR_TABLE.value] = True
                            row[Component.PINUP_MEDIA.value] = Verifier.verify_table_pinup_media_uninstall(
                                bdd_table_id=bdd_table_id,
                                bdd_table_version=bdd_table_version
                            )
                            row[Component.PINUP_VIDEOS.value] = Verifier.verify_table_pinup_videos_uninstall(
                                csv_table_videos_path=csv_table_videos_path,
                                bdd_table_id=bdd_table_id,
                                bdd_table_version=bdd_table_version
                            )
                            if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:
                                row[Component.CONFIG_XML.value] = Verifier.verify_table_xml_config_uninstall(
                                    bdd_table_id=bdd_table_id,
                                    bdd_table_version=bdd_table_version,
                                    bdd_table_rom=bdd_table_rom
                                )
                                row[Component.CONFIG_REG.value] = Verifier.verify_table_reg_config_uninstall(
                                    bdd_table_id=bdd_table_id,
                                    bdd_table_version=bdd_table_version,
                                    bdd_table_rom=bdd_table_rom
                                )

                            # Retrieve color
                            row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                                row=row
                            )

                            # Append row
                            table_top_rows.append(row)

                    case Action.EXPORT:

                        # Initialize progress bar
                        item_current_counter = 0
                        item_total_counter = self.__count_items_to_refresh(
                            items=bdd_tables
                        )
                        self.progress_bar.config(
                            maximum=item_total_counter
                        )

                        # Retrieve tables from BDD
                        for bdd_table in bdd_tables:
                            bdd_table_id = bdd_table[Constants.BDD_COL_TABLE_ID]
                            bdd_table_name = bdd_table[Constants.BDD_COL_TABLE_NAME]

                            # Ignore item to refresh if requested
                            if not self.__is_item_to_refresh(bdd_table_id):
                                continue

                            # Interrupt process if requested
                            if self.__interruption_requested:
                                self.__on_close()
                                return

                            # Increment progress bar
                            item_current_counter += 1
                            self.progress_bar['value'] = item_current_counter
                            self.progress_label.config(
                                text=Context.get_text(
                                    'refresh_in_progress',
                                    item_name=bdd_table_name,
                                    item_current_counter=item_current_counter,
                                    item_total_counter=item_total_counter
                                )
                            )

                            # Waiting 0.1 seconde to see the dialog if the process is quick
                            time.sleep(0.1)

                            # Retrieve BDD table's data
                            bdd_table_version = bdd_table[Constants.BDD_COL_TABLE_VERSION]
                            bdd_table_rom = bdd_table[Constants.BDD_COL_TABLE_ROM]

                            if Verifier.verify_none_value(bdd_table_version):
                                bdd_table_version = 'latest'

                            # Retrieve CSV Table
                            csv_table = ListHelper.select_item(
                                item_id=bdd_table_id,
                                a_list=csv_tables,
                                id_column=Constants.CSV_COL_ID
                            )
                            csv_table_videos_path = csv_table.get(
                                Constants.CSV_COL_VIDEOS_PATH,
                                None
                            )

                            # Retrieve CSV table's data
                            csv_table_version = csv_table.get(
                                Constants.CSV_COL_VERSION,
                                None
                            )
                            csv_table_rom = csv_table.get(
                                Constants.CSV_COL_ROM,
                                None
                            )

                            # Build row
                            row = {}
                            row[Constants.UI_TABLE_KEY_COL_SELECTION] = False
                            row[Constants.UI_TABLE_KEY_COL_ID] = bdd_table_id
                            row[Constants.UI_TABLE_KEY_COL_NAME] = bdd_table_name
                            row[Constants.UI_TABLE_KEY_COL_LATEST_VERSION] = Verifier.verify_csv_bdd_version(
                                csv_version=csv_table_version,
                                bdd_version=bdd_table_version
                            )
                            if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:
                                row[Component.EMULATOR_TABLE.value] = Verifier.verify_table_emulator_export(
                                    bdd_table_id=bdd_table_id,
                                    bdd_table_version=bdd_table_version,
                                    csv_table_rom=csv_table_rom
                                )
                            else:
                                row[Component.EMULATOR_TABLE.value] = row[Constants.UI_TABLE_KEY_COL_LATEST_VERSION]
                            row[Component.PINUP_MEDIA.value] = Verifier.verify_table_pinup_media_export(
                                bdd_table_id=bdd_table_id,
                                bdd_table_version=bdd_table_version
                            )
                            row[Component.PINUP_VIDEOS.value] = Verifier.verify_table_pinup_videos_export(
                                csv_table_videos_path=csv_table_videos_path,
                                bdd_table_id=bdd_table_id,
                                bdd_table_version=bdd_table_version
                            )
                            if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:
                                row[Component.CONFIG_XML.value] = Verifier.verify_table_xml_config_export(
                                    bdd_table_id=bdd_table_id,
                                    bdd_table_version=bdd_table_version,
                                    bdd_table_rom=bdd_table_rom
                                )
                                row[Component.CONFIG_REG.value] = Verifier.verify_table_reg_config_export(
                                    bdd_table_id=bdd_table_id,
                                    bdd_table_version=bdd_table_version,
                                    bdd_table_rom=bdd_table_rom
                                )

                            # Retrieve color
                            row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                                row=row
                            )

                            # Append row
                            table_top_rows.append(row)

                    case Action.COPY:

                        # Initialize progress bar
                        item_current_counter = 0
                        item_total_counter = self.__count_items_to_refresh(
                            items=csv_tables
                        )
                        self.progress_bar.config(
                            maximum=item_total_counter
                        )

                        # Retrieve tables from CSV
                        for csv_table in csv_tables:
                            csv_table_id = csv_table[Constants.CSV_COL_ID]
                            csv_table_name = csv_table[Constants.CSV_COL_NAME]

                            # Ignore item to refresh if requested
                            if not self.__is_item_to_refresh(csv_table_id):
                                continue

                            # Interrupt process if requested
                            if self.__interruption_requested:
                                self.__on_close()
                                return

                            # Increment progress bar
                            item_current_counter += 1
                            self.progress_bar['value'] = item_current_counter
                            self.progress_label.config(
                                text=Context.get_text(
                                    'refresh_in_progress',
                                    item_name=csv_table_name,
                                    item_current_counter=item_current_counter,
                                    item_total_counter=item_total_counter
                                )
                            )

                            # Waiting 0.1 seconde to see the dialog if the process is quick
                            time.sleep(0.1)

                            # Retrieve CSV table's data
                            csv_table_version = csv_table[Constants.CSV_COL_VERSION]
                            csv_table_rom = csv_table[Constants.CSV_COL_ROM]
                            csv_table_videos_path = csv_table[Constants.CSV_COL_VIDEOS_PATH]

                            # Retrieve BDD Table
                            bdd_table = ListHelper.select_item(
                                item_id=csv_table_id,
                                a_list=bdd_tables,
                                id_column=Constants.BDD_COL_TABLE_ID
                            )

                            # Retrieve BDD table's data
                            bdd_table_id = bdd_table.get(
                                Constants.BDD_COL_TABLE_ID,
                                None
                            )
                            bdd_table_version = bdd_table.get(
                                Constants.BDD_COL_TABLE_VERSION,
                                None
                            )

                            # Build row
                            row = {}
                            row[Constants.UI_TABLE_KEY_COL_SELECTION] = False
                            row[Constants.UI_TABLE_KEY_COL_ID] = csv_table_id
                            row[Constants.UI_TABLE_KEY_COL_NAME] = csv_table_name

                            # Retrieve color
                            row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                                row=row
                            )

                            # Append row
                            table_top_rows.append(row)

                    case Action.EDIT:

                        # Initialize progress bar
                        item_current_counter = 0
                        item_total_counter = self.__count_items_to_refresh(
                            items=csv_tables
                        )
                        self.progress_bar.config(
                            maximum=item_total_counter
                        )

                        # Retrieve tables from CSV
                        for csv_table in csv_tables:
                            csv_table_id = csv_table[Constants.CSV_COL_ID]
                            csv_table_name = csv_table[Constants.CSV_COL_NAME]

                            # Ignore item to refresh if requested
                            if not self.__is_item_to_refresh(csv_table_id):
                                continue

                            # Interrupt process if requested
                            if self.__interruption_requested:

                                # Destroy Selenium Web Browser
                                Context.destroy_selenium_web_browser()

                                self.__on_close()
                                return

                            # Increment progress bar
                            item_current_counter += 1
                            self.progress_bar['value'] = item_current_counter
                            self.progress_label.config(
                                text=Context.get_text(
                                    'refresh_in_progress',
                                    item_name=csv_table_name,
                                    item_current_counter=item_current_counter,
                                    item_total_counter=item_total_counter
                                )
                            )

                            # Waiting 0.1 seconde to see the dialog if the process is quick
                            time.sleep(0.1)

                            # Retrieve CSV table's data
                            csv_table_version = csv_table[Constants.CSV_COL_VERSION]
                            csv_table_rom = csv_table[Constants.CSV_COL_ROM]
                            csv_table_videos_path = csv_table[Constants.CSV_COL_VIDEOS_PATH]
                            csv_table_weblink_url = csv_table[Constants.CSV_COL_WEBLINK_URL]

                            # Build row
                            row = {}
                            row[Constants.UI_TABLE_KEY_COL_SELECTION] = False
                            row[Constants.UI_TABLE_KEY_COL_ID] = csv_table_id
                            row[Constants.UI_TABLE_KEY_COL_NAME] = csv_table_name
                            (row[Constants.UI_TABLE_KEY_COL_LATEST_VERSION],
                             row[Constants.UI_TABLE_KEY_COL_UNIQUE_VERSION]) = Verifier.verify_table_versions(
                                csv_table_id=csv_table_id,
                                csv_table_weblink_url=csv_table_weblink_url
                            )
                            row[Component.PINUP_MEDIA.value] = Verifier.verify_table_pinup_media_edit(
                                csv_table_id=csv_table_id,
                                csv_table_version=csv_table_version
                            )
                            row[Component.PINUP_VIDEOS.value] = Verifier.verify_table_pinup_videos_edit(
                                csv_table_videos_path=csv_table_videos_path,
                                csv_table_id=csv_table_id,
                                csv_table_version=csv_table_version
                            )

                            # Retrieve color
                            row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                                row=row
                            )

                            # Append row
                            table_top_rows.append(row)

                        # Destroy Selenium Web Browser
                        Context.destroy_selenium_web_browser()

            case Category.PLAYLISTS:
                # Append row for each playlist
                csv_playlists = CsvHelper.read_data(
                    file_path=Context.get_csv_path()
                )
                bdd_playlists = BddHelper.list_playlists(
                    bdd_file_path=Context.get_pinup_bdd_path()
                )

                match(Context.get_selected_action()):
                    case Action.INSTALL:

                        # Initialize progress bar
                        item_current_counter = 0
                        item_total_counter = self.__count_items_to_refresh(
                            items=csv_playlists
                        )
                        self.progress_bar.config(
                            maximum=item_total_counter
                        )

                        # Retrieve playlists from CSV
                        for csv_playlist in csv_playlists:
                            csv_playlist_id = csv_playlist[Constants.CSV_COL_ID]
                            csv_playlist_name = csv_playlist[Constants.CSV_COL_NAME]

                            # Ignore item to refresh if requested
                            if not self.__is_item_to_refresh(csv_playlist_id):
                                continue

                            # Interrupt process if requested
                            if self.__interruption_requested:
                                self.__on_close()
                                return

                            # Increment progress bar
                            item_current_counter += 1
                            self.progress_bar['value'] = item_current_counter
                            self.progress_label.config(
                                text=Context.get_text(
                                    'refresh_in_progress',
                                    item_name=csv_playlist_name,
                                    item_current_counter=item_current_counter,
                                    item_total_counter=item_total_counter
                                )
                            )

                            # Waiting 0.1 seconde to see the dialog if the process is quick
                            time.sleep(0.1)

                            # Retrieve CSV playlist's data
                            csv_playlist_version = csv_playlist[Constants.CSV_COL_VERSION]

                            # Retrieve BDD Playlist
                            bdd_playlist = ListHelper.select_item(
                                item_id=csv_playlist_id,
                                a_list=bdd_playlists,
                                id_column=Constants.BDD_COL_PLAYLIST_ID
                            )

                            # Retrieve BDD playlist's data
                            bdd_playlist_version = bdd_playlist.get(
                                Constants.BDD_COL_PLAYLIST_VERSION,
                                None
                            )

                            # Build row
                            row = {}
                            row[Constants.UI_TABLE_KEY_COL_SELECTION] = False
                            row[Constants.UI_TABLE_KEY_COL_ID] = csv_playlist_id
                            row[Constants.UI_TABLE_KEY_COL_NAME] = csv_playlist_name
                            row[Constants.UI_TABLE_KEY_COL_LATEST_VERSION] = Verifier.verify_csv_bdd_version(
                                csv_version=csv_playlist_version,
                                bdd_version=bdd_playlist_version
                            )
                            row[Component.EMULATOR_PLAYLIST.value] = not Verifier.verify_none_value(
                                bdd_playlist_version
                            )
                            row[Component.PINUP_MEDIA.value] = Verifier.verify_playlist_pinup_media_install(
                                csv_playlist_id=csv_playlist_id
                            )

                            # Retrieve color
                            row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                                row=row
                            )

                            # Append row
                            table_top_rows.append(row)

                    case Action.UNINSTALL:

                        # Initialize progress bar
                        item_current_counter = 0
                        item_total_counter = self.__count_items_to_refresh(
                            items=bdd_playlists
                        )
                        self.progress_bar.config(
                            maximum=item_total_counter
                        )

                        # Retrieve playlists from BDD
                        for bdd_playlist in bdd_playlists:
                            bdd_playlist_id = bdd_playlist[Constants.BDD_COL_PLAYLIST_ID]
                            bdd_playlist_name = bdd_playlist[Constants.BDD_COL_PLAYLIST_NAME]

                            # Ignore item to refresh if requested
                            if not self.__is_item_to_refresh(bdd_playlist_id):
                                continue

                            # Interrupt process if requested
                            if self.__interruption_requested:
                                self.__on_close()
                                return

                            # Increment progress bar
                            item_current_counter += 1
                            self.progress_bar['value'] = item_current_counter
                            self.progress_label.config(
                                text=Context.get_text(
                                    'refresh_in_progress',
                                    item_name=bdd_playlist_name,
                                    item_current_counter=item_current_counter,
                                    item_total_counter=item_total_counter
                                )
                            )

                            # Waiting 0.1 seconde to see the dialog if the process is quick
                            time.sleep(0.1)

                            # Retrieve BDD playlist's data
                            bdd_playlist_version = bdd_playlist[Constants.BDD_COL_PLAYLIST_VERSION]

                            if Verifier.verify_none_value(bdd_playlist_version):
                                bdd_playlist_version = 'latest'

                            # Retrieve CSV Playlist
                            csv_playlist = ListHelper.select_item(
                                item_id=bdd_playlist_id,
                                a_list=csv_playlists,
                                id_column=Constants.CSV_COL_ID
                            )

                            # Retrieve BDD playlist's data
                            csv_playlist_version = csv_playlist.get(
                                Constants.CSV_COL_VERSION,
                                None
                            )

                            # Build row
                            row = {}
                            row[Constants.UI_TABLE_KEY_COL_SELECTION] = False
                            row[Constants.UI_TABLE_KEY_COL_ID] = bdd_playlist_id
                            row[Constants.UI_TABLE_KEY_COL_NAME] = bdd_playlist_name
                            row[Component.EMULATOR_PLAYLIST.value] = Verifier.verify_none_value(
                                bdd_playlist_version
                            )
                            row[Component.PINUP_MEDIA.value] = Verifier.verify_playlist_pinup_media_uninstall(
                                bdd_playlist_id=bdd_playlist_id
                            )

                            # Retrieve color
                            row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                                row=row
                            )

                            # Append row
                            table_top_rows.append(row)

                    case Action.EXPORT:

                        # Initialize progress bar
                        item_current_counter = 0
                        item_total_counter = self.__count_items_to_refresh(
                            items=bdd_playlists
                        )
                        self.progress_bar.config(
                            maximum=item_total_counter
                        )

                        # Retrieve playlists from BDD
                        for bdd_playlist in bdd_playlists:
                            bdd_playlist_id = bdd_playlist[Constants.BDD_COL_PLAYLIST_ID]
                            bdd_playlist_name = bdd_playlist[Constants.BDD_COL_PLAYLIST_NAME]

                            # Ignore item to refresh if requested
                            if not self.__is_item_to_refresh(bdd_playlist_id):
                                continue

                            # Interrupt process if requested
                            if self.__interruption_requested:
                                self.__on_close()
                                return

                            # Increment progress bar
                            item_current_counter += 1
                            self.progress_bar['value'] = item_current_counter
                            self.progress_label.config(
                                text=Context.get_text(
                                    'refresh_in_progress',
                                    item_name=bdd_playlist_name,
                                    item_current_counter=item_current_counter,
                                    item_total_counter=item_total_counter
                                )
                            )

                            # Waiting 0.1 seconde to see the dialog if the process is quick
                            time.sleep(0.1)

                            # Retrieve BDD playlist's data
                            bdd_playlist_version = bdd_playlist[Constants.BDD_COL_PLAYLIST_VERSION]

                            if Verifier.verify_none_value(bdd_playlist_version):
                                bdd_playlist_version = 'latest'

                            # Retrieve CSV Playlist
                            csv_playlist = ListHelper.select_item(
                                item_id=bdd_playlist_id,
                                a_list=csv_playlists,
                                id_column=Constants.CSV_COL_ID
                            )

                            # Retrieve BDD playlist's data
                            csv_playlist_version = csv_playlist.get(
                                Constants.CSV_COL_VERSION,
                                None
                            )

                            # Build row
                            row = {}
                            row[Constants.UI_TABLE_KEY_COL_SELECTION] = False
                            row[Constants.UI_TABLE_KEY_COL_ID] = bdd_playlist_id
                            row[Constants.UI_TABLE_KEY_COL_NAME] = bdd_playlist_name
                            row[Constants.UI_TABLE_KEY_COL_LATEST_VERSION] = Verifier.verify_csv_bdd_version(
                                csv_version=csv_playlist_version,
                                bdd_version=bdd_playlist_version
                            )
                            row[Component.EMULATOR_PLAYLIST.value] = Verifier.verify_playlist_emulator_export(
                                bdd_playlist_id=bdd_playlist_id,
                                bdd_playlist_version=bdd_playlist_version
                            )
                            row[Component.PINUP_MEDIA.value] = Verifier.verify_playlist_pinup_media_export(
                                bdd_playlist_id=bdd_playlist_id,
                                bdd_playlist_version=bdd_playlist_version
                            )

                            # Retrieve color
                            row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                                row=row
                            )

                            # Append row
                            table_top_rows.append(row)

                    case Action.COPY:

                        # Initialize progress bar
                        item_current_counter = 0
                        item_total_counter = self.__count_items_to_refresh(
                            items=csv_playlists
                        )
                        self.progress_bar.config(
                            maximum=item_total_counter
                        )

                        # Retrieve playlists from CSV
                        for csv_playlist in csv_playlists:
                            csv_playlist_id = csv_playlist[Constants.CSV_COL_ID]
                            csv_playlist_name = csv_playlist[Constants.CSV_COL_NAME]

                            # Ignore item to refresh if requested
                            if not self.__is_item_to_refresh(csv_playlist_id):
                                continue

                            # Interrupt process if requested
                            if self.__interruption_requested:
                                self.__on_close()
                                return

                            # Increment progress bar
                            item_current_counter += 1
                            self.progress_bar['value'] = item_current_counter
                            self.progress_label.config(
                                text=Context.get_text(
                                    'refresh_in_progress',
                                    item_name=csv_playlist_name,
                                    item_current_counter=item_current_counter,
                                    item_total_counter=item_total_counter
                                )
                            )

                            # Waiting 0.1 seconde to see the dialog if the process is quick
                            time.sleep(0.1)

                            # Build row
                            row = {}
                            row[Constants.UI_TABLE_KEY_COL_SELECTION] = False
                            row[Constants.UI_TABLE_KEY_COL_ID] = csv_playlist_id
                            row[Constants.UI_TABLE_KEY_COL_NAME] = csv_playlist_name

                            # Retrieve color
                            row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                                row=row
                            )

                            # Append row
                            table_top_rows.append(row)

                    case Action.EDIT:

                        # Initialize progress bar
                        item_current_counter = 0
                        item_total_counter = self.__count_items_to_refresh(
                            items=csv_playlists
                        )
                        self.progress_bar.config(
                            maximum=item_total_counter
                        )

                        # Retrieve playlists from CSV
                        for csv_playlist in csv_playlists:
                            csv_playlist_id = csv_playlist[Constants.CSV_COL_ID]
                            csv_playlist_name = csv_playlist[Constants.CSV_COL_NAME]

                            # Ignore item to refresh if requested
                            if not self.__is_item_to_refresh(csv_playlist_id):
                                continue

                            # Interrupt process if requested
                            if self.__interruption_requested:
                                self.__on_close()
                                return

                            # Increment progress bar
                            item_current_counter += 1
                            self.progress_bar['value'] = item_current_counter
                            self.progress_label.config(
                                text=Context.get_text(
                                    'refresh_in_progress',
                                    item_name=csv_playlist_name,
                                    item_current_counter=item_current_counter,
                                    item_total_counter=item_total_counter
                                )
                            )

                            # Waiting 0.1 seconde to see the dialog if the process is quick
                            time.sleep(0.1)

                            # Retrieve CSV playlist's data
                            csv_playlist_version = csv_playlist[Constants.CSV_COL_VERSION]

                            # Build row
                            row = {}
                            row[Constants.UI_TABLE_KEY_COL_SELECTION] = False
                            row[Constants.UI_TABLE_KEY_COL_ID] = csv_playlist_id
                            row[Constants.UI_TABLE_KEY_COL_NAME] = csv_playlist_name
                            row[Constants.UI_TABLE_KEY_COL_UNIQUE_VERSION] = Verifier.verify_playlist_version(
                                csv_playlist_id=csv_playlist_id
                            )
                            row[Component.PINUP_MEDIA.value] = Verifier.verify_playlist_pinup_media_edit(
                                csv_playlist_id=csv_playlist_id,
                                csv_playlist_version=csv_playlist_version
                            )

                            # Retrieve color
                            row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                                row=row
                            )

                            # Append row
                            table_top_rows.append(row)

            case Category.BDD_TABLES:
                bdd_tables = BddHelper.list_bdd_tables(
                    bdd_file_path=Context.get_pinup_bdd_path()
                )

                match(Context.get_selected_action()):
                    case Action.INSTALL:

                        # Initialize progress bar
                        item_current_counter = 0
                        item_total_counter = self.__count_items_to_refresh(
                            items=Constants.PINUP_BDD_TABLES
                        )
                        self.progress_bar.config(
                            maximum=item_total_counter
                        )

                        for bdd_table in Constants.PINUP_BDD_TABLES:

                            # Ignore item to refresh if requested
                            if not self.__is_item_to_refresh(bdd_table):
                                continue

                            # Interrupt process if requested
                            if self.__interruption_requested:
                                self.__on_close()
                                return

                            # Increment progress bar
                            item_current_counter += 1
                            self.progress_bar['value'] = item_current_counter
                            self.progress_label.config(
                                text=Context.get_text(
                                    'refresh_in_progress',
                                    item_name=bdd_table,
                                    item_current_counter=item_current_counter,
                                    item_total_counter=item_total_counter
                                )
                            )

                            # Waiting 0.1 seconde to see the dialog if the process is quick
                            time.sleep(0.1)

                            # Build row
                            row = {}
                            row[Constants.UI_TABLE_KEY_COL_SELECTION] = False
                            row[Constants.UI_TABLE_KEY_COL_ID] = bdd_table
                            row[Constants.UI_TABLE_KEY_COL_NAME] = row[Constants.UI_TABLE_KEY_COL_ID]
                            row[Component.PINUP_DATABASE.value] = Verifier.verify_bdd_table(
                                bdd_tables=bdd_tables,
                                bdd_table=bdd_table
                            )

                            # Retrieve color
                            row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                                row=row
                            )

                            # Append row
                            table_top_rows.append(row)

                    case Action.UNINSTALL:

                        # Initialize progress bar
                        item_current_counter = 0
                        item_total_counter = self.__count_items_to_refresh(
                            items=Constants.PINUP_BDD_TABLES
                        )
                        self.progress_bar.config(
                            maximum=item_total_counter
                        )

                        for bdd_table in Constants.PINUP_BDD_TABLES:

                            # Ignore item to refresh if requested
                            if not self.__is_item_to_refresh(bdd_table):
                                continue

                            # Interrupt process if requested
                            if self.__interruption_requested:
                                self.__on_close()
                                return

                            # Increment progress bar
                            item_current_counter += 1
                            self.progress_bar['value'] = item_current_counter
                            self.progress_label.config(
                                text=Context.get_text(
                                    'refresh_in_progress',
                                    item_name=bdd_table,
                                    item_current_counter=item_current_counter,
                                    item_total_counter=item_total_counter
                                )
                            )

                            # Waiting 0.1 seconde to see the dialog if the process is quick
                            time.sleep(0.1)

                            # Build row
                            row = {}
                            row[Constants.UI_TABLE_KEY_COL_SELECTION] = False
                            row[Constants.UI_TABLE_KEY_COL_ID] = bdd_table
                            row[Constants.UI_TABLE_KEY_COL_NAME] = row[Constants.UI_TABLE_KEY_COL_ID]
                            row[Component.PINUP_DATABASE.value] = not Verifier.verify_bdd_table(
                                bdd_tables=bdd_tables,
                                bdd_table=bdd_table
                            )

                            # Retrieve color
                            row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                                row=row
                            )

                            # Append row
                            table_top_rows.append(row)

                    case Action.EXPORT:

                        # Initialize progress bar
                        item_current_counter = 0
                        item_total_counter = self.__count_items_to_refresh(
                            items=Constants.PINUP_BDD_TABLES
                        )
                        self.progress_bar.config(
                            maximum=item_total_counter
                        )

                        for bdd_table in Constants.PINUP_BDD_TABLES:

                            # Ignore item to refresh if requested
                            if not self.__is_item_to_refresh(bdd_table):
                                continue

                            # Interrupt process if requested
                            if self.__interruption_requested:
                                self.__on_close()
                                return

                            # Increment progress bar
                            item_current_counter += 1
                            self.progress_bar['value'] = item_current_counter
                            self.progress_label.config(
                                text=Context.get_text(
                                    'refresh_in_progress',
                                    item_name=bdd_table,
                                    item_current_counter=item_current_counter,
                                    item_total_counter=item_total_counter
                                )
                            )

                            # Waiting 0.1 seconde to see the dialog if the process is quick
                            time.sleep(0.1)

                            # Build row
                            row = {}
                            row[Constants.UI_TABLE_KEY_COL_SELECTION] = False
                            row[Constants.UI_TABLE_KEY_COL_ID] = bdd_table
                            row[Constants.UI_TABLE_KEY_COL_NAME] = row[Constants.UI_TABLE_KEY_COL_ID]
                            row[Component.PINUP_DATABASE.value] = True

                            # Retrieve color
                            row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                                row=row
                            )

                            # Append row
                            table_top_rows.append(row)

            case Category.CONFIGS:
                # Create the configs directory if it doesn't exist
                if not os.path.exists(Context.get_configs_path()):
                    os.makedirs(Context.get_configs_path())

                configs_paths = FileHelper.list_sub_directories(
                    folder_path=Context.get_configs_path()
                )

                # Initialize progress bar
                item_current_counter = 0
                item_total_counter = self.__count_items_to_refresh(
                    items=configs_paths
                )
                self.progress_bar.config(
                    maximum=item_total_counter
                )

                for config in configs_paths:

                    # Ignore item to refresh if requested
                    if not self.__is_item_to_refresh(config):
                        continue

                    # Interrupt process if requested
                    if self.__interruption_requested:
                        self.__on_close()
                        return

                    # Increment progress bar
                    item_current_counter += 1
                    self.progress_bar['value'] = item_current_counter
                    self.progress_label.config(
                        text=Context.get_text(
                            'refresh_in_progress',
                            item_name=config,
                            item_current_counter=item_current_counter,
                            item_total_counter=item_total_counter
                        )
                    )

                    # Waiting 0.1 seconde to see the dialog if the process is quick
                    time.sleep(0.1)

                    # Build row
                    row = {}
                    row[Constants.UI_TABLE_KEY_COL_SELECTION] = False
                    row[Constants.UI_TABLE_KEY_COL_ID] = config
                    row[Constants.UI_TABLE_KEY_COL_NAME] = config

                    match(Context.get_selected_action()):
                        case Action.INSTALL:
                            row[Component.FILES.value] = Verifier.verify_config_files_install(
                                config=config
                            )
                            row[Component.REGISTRY.value] = Verifier.verify_config_registry_install(
                                config=config
                            )

                        case Action.UNINSTALL:
                            row[Component.FILES.value] = Verifier.verify_config_files_uninstall(
                                config=config
                            )
                            row[Component.REGISTRY.value] = Verifier.verify_config_registry_uninstall(
                                config=config
                            )

                        case Action.EXPORT:
                            row[Component.FILES.value] = Verifier.verify_config_files_export(
                                config=config
                            )
                            row[Component.REGISTRY.value] = Verifier.verify_config_registry_export(
                                config=config
                            )

                        case Action.EDIT:
                            row[Component.FILES.value] = Verifier.verify_config_files_edit(
                                config=config
                            )
                            row[Component.REGISTRY.value] = Verifier.verify_config_registry_edit(
                                config=config
                            )

                    # Retrieve color
                    row[Constants.UI_TABLE_KEY_COLOR] = Verifier.retrieve_verified_row_color(
                        row=row
                    )

                    # Append row
                    table_top_rows.append(row)

        # Create refresh file path if missing
        refresh_file_path = Context.get_selected_rows_csv_path()
        refresh_file_path.parent.mkdir(parents=True, exist_ok=True)

        # If with only ids, add rows not refreshed from CSV rows
        if self.__is_with_only_ids():
            for row in CsvHelper.read_data(
                file_path=refresh_file_path,
            ):
                if self.__is_item_to_refresh(
                    item_id=row[Constants.UI_TABLE_KEY_COL_ID]
                ):
                    continue

                table_top_rows.append(row)

        # Sort rows depending on UI_TABLE_KEY_COLOR (desc) and Constants.UI_TABLE_KEY_COL_NAME (asc)
        sorted_rows = sorted(
            table_top_rows,
            key=lambda x: (-ord(
                x[Constants.UI_TABLE_KEY_COLOR][0]),
                x[Constants.UI_TABLE_KEY_COL_NAME]
            )
        )

        # Write data in a CSV file
        csv_rows = []
        for row in sorted_rows:
            csv_row = {}
            for key, value in row.items():
                if isinstance(value, bool):
                    if value:
                        csv_row[key] = Constants.CSV_YES_VALUE
                    else:
                        csv_row[key] = Constants.CSV_NO_VALUE
                else:
                    csv_row[key] = value
            csv_rows.append(csv_row)

        # Write data in a CSV file
        CsvHelper.write_data(
            file_path=refresh_file_path,
            data=csv_rows,
            sort_column_id=''
        )

        # Finish progression
        if item_total_counter > 0:
            self.progress_bar['value'] = item_total_counter
        else:
            self.progress_bar.config(maximum=1)
            self.progress_bar['value'] = 1
        self.progress_label.config(
            text=Context.get_text('refresh_finished')
        )

        # Specify that refresh is done
        self.__refresh_done = True

        # Close automatically
        self.__on_close()

    def __on_close(self):
        """Called when closing"""

        if self.__refresh_done or self.__interruption_requested:
            # Call back
            self.__callback()

            # Close the dialog
            UIHelper.close_dialog(self.dialog)
        else:
            # Ask if interrupt
            if messagebox.askyesno(
                Context.get_text('question'),
                Context.get_text('question_interrupt_process'),
                parent=self.dialog
            ):
                self.__interruption_requested = True

    def __is_with_only_ids(
        self
    ):
        """Specify if with only ids"""

        return self.__only_ids is not None and \
            len(self.__only_ids) > 0

    def __is_item_to_refresh(
        self,
        item_id: str
    ):
        """Specify if the id has to be refreshed"""

        if self.__is_with_only_ids():
            return item_id in self.__only_ids

        return True

    def __count_items_to_refresh(
        self,
        items: list
    ):
        """Count how many items to refresh"""

        if self.__is_with_only_ids():
            return len(self.__only_ids)

        return len(items)
