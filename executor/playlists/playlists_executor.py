#!/usr/bin/python3
"""Executor to manage Playlists"""


import os
from pathlib import Path
from executor.abstract_executor import AbstractExecutor
from libraries.constants.constants import Action, Component, Constants
from libraries.context.context import Context
from libraries.csv.csv_helper import CsvHelper
from libraries.bdd.bdd_helper import BddHelper
from libraries.file.file_helper import FileHelper
from libraries.list.list_helper import ListHelper


class PlaylistsExecutor(AbstractExecutor):
    """Executor to manage Playlists"""

    def __list_media_cache_relative_paths(self):
        """List media cache paths"""

        result = []
        for cache_file_name in Constants.CACHE_FILES_NAMES:
            result.extend(FileHelper.list_relative_paths(
                folder_path=Context.get_pinup_media_path(),
                file_name=f'*{cache_file_name}*',
                error_if_not_found=False
            ))
        return result

    def __get_data_media_path(
        self,
        playlist_id: str,
        playlist_version: str
    ):
        """Get data media path"""

        return Path(os.path.join(
            Context.get_working_path(),
            'playlists',
            playlist_id,
            playlist_version,
            'media'
        ))

    def __execute_uninstall(
        self,
        bdd_item: dict
    ):
        """Execute uninstall"""

        if bdd_item is None:
            return

        # Retrieve playlist's data
        playlist_id = bdd_item[Constants.BDD_COL_PLAYLIST_ID]

        # Delete playlist
        if Component.EMULATOR_PLAYLIST in Context.get_selected_components():

            BddHelper.delete_playlist(
                bdd_file_path=Context.get_pinup_bdd_path(),
                playlist=bdd_item
            )

        # Delete media files
        if Component.PINUP_MEDIA in Context.get_selected_components():

            relative_paths = FileHelper.list_relative_paths(
                folder_path=Context.get_pinup_media_path(),
                file_name=playlist_id,
                error_if_not_found=False
            )
            for relative_path in relative_paths:
                FileHelper.delete_file(
                    file_path=os.path.join(
                        Context.get_pinup_media_path(),
                        relative_path
                    )
                )

            # Delete pup cache files
            relative_paths = self.__list_media_cache_relative_paths()
            for relative_path in relative_paths:
                FileHelper.delete_file(
                    file_path=os.path.join(
                        Context.get_pinup_media_path(),
                        relative_path
                    )
                )

    def __execute_install(
        self,
        csv_item: dict
    ):
        """Execute install"""

        if csv_item is None:
            return

        # Retrieve playlist's data
        playlist_id = csv_item[Constants.CSV_COL_ID]
        playlist_version = csv_item[Constants.CSV_COL_VERSION]

        # Check that the playlist exists in data
        if not self.__get_data_media_path(
            playlist_id=playlist_id,
            playlist_version=playlist_version
        ).exists():
            raise Exception(Context.get_text(
                'error_missing_playlist',
                playlist_version=playlist_version
            ))

        # Insert playlist
        if Component.EMULATOR_PLAYLIST in Context.get_selected_components():

            BddHelper.insert_playlist(
                bdd_file_path=Context.get_pinup_bdd_path(),
                playlist_data=csv_item
            )

        # Insert media files
        if Component.PINUP_MEDIA in Context.get_selected_components():

            source_folder_path = self.__get_data_media_path(
                playlist_id=playlist_id,
                playlist_version=playlist_version
            )
            destination_folder_path = Context.get_pinup_media_path()
            relative_paths = FileHelper.list_relative_paths(
                folder_path=source_folder_path,
                file_name=playlist_id
            )
            for relative_path in relative_paths:
                FileHelper.copy_file(
                    source_file_path=os.path.join(
                        source_folder_path,
                        relative_path
                    ),
                    destination_file_path=os.path.join(
                        destination_folder_path,
                        relative_path
                    )
                )

    def __execute_export(
        self,
        bdd_item: dict
    ):
        """Execute export"""

        if bdd_item is None:
            return

        # Retrieve playlist's data
        playlist_id = ListHelper.format_value(
            bdd_item[Constants.BDD_COL_PLAYLIST_ID]
        )
        playlist_name = ListHelper.format_value(
            bdd_item[Constants.BDD_COL_PLAYLIST_NAME]
        )
        playlist_sql = bdd_item['PlayListSQL']

        # Export media files
        if Component.PINUP_MEDIA in Context.get_selected_components():

            source_folder_path = Context.get_pinup_media_path()
            destination_folder_path = self.__get_data_media_path(
                playlist_id=playlist_id,
                playlist_version=Constants.LATEST_PATH
            )
            relative_paths = FileHelper.list_relative_paths(
                folder_path=source_folder_path,
                file_name=playlist_id
            )
            for relative_path in relative_paths:
                FileHelper.copy_file(
                    source_file_path=os.path.join(
                        source_folder_path,
                        relative_path
                    ),
                    destination_file_path=os.path.join(
                        destination_folder_path,
                        relative_path
                    )
                )

        # Write data in CSV
        csv_playlists = ListHelper.replace_item(
            a_list=CsvHelper.read_data(
                file_path=Context.get_csv_path()
            ),
            item={
                Constants.CSV_COL_AVAILABLE: Constants.CSV_YES_VALUE,
                Constants.CSV_COL_VERSION: Constants.LATEST_PATH,
                Constants.CSV_COL_NAME: playlist_name,
                Constants.CSV_COL_ID: playlist_id,
                Constants.CSV_COL_SQL: playlist_sql
            },
            id_column=Constants.CSV_COL_ID
        )
        CsvHelper.write_data(
            file_path=Context.get_csv_path(),
            data=csv_playlists
        )

    def __execute_copy(
        self,
        csv_item: dict
    ):
        """Execute copy"""

        if csv_item is None:
            return

        # Retrieve playlist's data
        playlist_id = csv_item[Constants.CSV_COL_ID]
        playlist_version = csv_item[Constants.CSV_COL_VERSION]

        # Check that the playlist exists in data
        if not self.__get_data_media_path(
            playlist_id=playlist_id,
            playlist_version=playlist_version
        ).exists():
            raise Exception(Context.get_text(
                'error_missing_playlist',
                playlist_version=playlist_version
            ))

        # Copy playlist
        if Component.EMULATOR_PLAYLIST in Context.get_selected_components():

            # Copy item in a CSV file
            CsvHelper.write_data(
                file_path=os.path.join(
                    self.get_copy_folder_path(),
                    playlist_id,
                    'database.csv'
                ),
                data=[csv_item]
            )

        # Copy media files
        if Component.PINUP_MEDIA in Context.get_selected_components():

            source_folder_path = self.__get_data_media_path(
                playlist_id=playlist_id,
                playlist_version=playlist_version
            )
            destination_folder_path = os.path.join(
                self.get_copy_folder_path(),
                playlist_id,
                'media'
            )
            FileHelper.copy_folder(
                source_folder_path=source_folder_path,
                destination_folder_path=destination_folder_path
            )

    def do_execution(self, item_id: str):
        """Do execution for an item"""

        # Retrieve CSV item
        csv_item = ListHelper.select_item(
            item_id=item_id,
            a_list=CsvHelper.read_data(
                file_path=Context.get_csv_path()
            ),
            id_column=Constants.CSV_COL_ID
        )

        # Retrieve bdd item
        bdd_item = BddHelper.get_playlist(
            bdd_file_path=Context.get_pinup_bdd_path(),
            playlist_id=item_id
        )

        match(Context.get_selected_action()):
            case Action.UNINSTALL:
                self.__execute_uninstall(
                    bdd_item=bdd_item
                )

            case Action.INSTALL:
                self.__execute_uninstall(
                    bdd_item=bdd_item
                )
                self.__execute_install(
                    csv_item=csv_item
                )

            case Action.EXPORT:
                self.__execute_export(
                    bdd_item=bdd_item
                )

            case Action.COPY:
                self.__execute_copy(
                    csv_item=csv_item
                )
