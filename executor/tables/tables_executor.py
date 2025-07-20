#!/usr/bin/python3
"""Executor to manage Tables"""

import os
from pathlib import Path
import re
from executor.abstract_executor import AbstractExecutor
from libraries.cmd.cmd_helper import CmdHelper
from libraries.constants.constants import Action, Component, Constants, Emulator
from libraries.csv.csv_helper import CsvHelper
from libraries.bdd.bdd_helper import BddHelper
from libraries.context.context import Context
from libraries.file.file_helper import FileHelper
from libraries.list.list_helper import ListHelper
from libraries.winreg.winreg_helper import WinRegHelper
from libraries.xml.xml_helper import XmlHelper

# pylint: disable=too-many-nested-blocks, too-many-locals
# pylint: disable=too-many-statements, too-many-branches


class TablesExecutor(AbstractExecutor):
    """Executor to manage Tables"""

    def __get_data_emulator_path(
        self,
        table_id: str,
        table_version: str
    ):
        """Get data emulator path"""

        return Path(os.path.join(
            Context.get_working_path(),
            'tables',
            Context.get_selected_emulator().value,
            table_id,
            table_version,
            'emulator'
        ))

    def __get_data_media_path(
        self,
        table_id: str,
        table_version: str
    ):
        """Get data media path"""

        return Path(os.path.join(
            Context.get_working_path(),
            'tables',
            Context.get_selected_emulator().value,
            table_id,
            table_version,
            'media'
        ))

    def __get_data_xml_config_path(
        self,
        table_id: str,
        table_version: str
    ):
        """Get data XML config path"""

        if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:
            return Path(os.path.join(
                Context.get_working_path(),
                'tables',
                Emulator.VISUAL_PINBALL_X.value,
                table_id,
                table_version,
                'config',
                'B2STableSettings.xml'
            ))

        return None

    def __get_data_pinup_videos_path(
        self,
        table_id: str,
        table_version: str,
        table_videos_path: str
    ):
        """Get data pinup video path"""

        return Path(os.path.join(
            Context.get_working_path(),
            'tables',
            Context.get_selected_emulator().value,
            table_id,
            table_version,
            'PUPVideos',
            table_videos_path
        ))

    def __get_data_reg_file_path(
        self,
        table_id: str,
        table_version: str
    ):
        """Get data regedit file path"""

        if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:
            return Path(os.path.join(
                Context.get_working_path(),
                'tables',
                Emulator.VISUAL_PINBALL_X.value,
                table_id,
                table_version,
                'config',
                f'user_values{Constants.REGEDIT_FILE_EXTENSION}'
            ))

        return None

    def __get_pinup_videos_path(
        self,
        table_videos_path: str
    ):
        """Return the pinup video path"""

        return Path(os.path.join(
            Context.get_pinup_path(),
            'PUPVideos',
            table_videos_path
        ))

    def __get_xml_config_path(self):
        """Get XML config path"""

        if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:
            return Path(os.path.join(
                Context.get_emulator_path(
                    Context.get_selected_emulator()
                ),
                'Tables',
                'B2STableSettings.xml'
            ))

        return None

    def __get_extract_cmd(
        self,
        table_alt_exe: str
    ):
        """Get command to extract script"""

        if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:
            extract_exe_path = os.path.join(
                Context.get_emulator_path(Emulator.VISUAL_PINBALL_X),
                table_alt_exe
            )
            return f'"{extract_exe_path}" -Minimized -ExtractVBS'

        return None

    def __list_tables_relative_paths(
        self,
        folder_path: str,
        table_id: str
    ):
        """List relative paths for the specified table"""

        relative_paths = FileHelper.list_relative_paths(
            folder_path=folder_path,
            file_name=table_id,
            error_if_not_found=False
        )

        for table_suffix in [' Fulldmd', '*(SCREEN*']:
            relative_paths.extend(FileHelper.list_relative_paths(
                folder_path=folder_path,
                file_name=f'{table_id}{table_suffix}',
                error_if_not_found=False
            ))

        return relative_paths

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

    def __execute_uninstall(
        self,
        bdd_item: dict,
        csv_item: dict
    ):
        """Execute uninstall"""

        if bdd_item is None:
            return

        # Retrieve table's data
        table_id = ListHelper.format_value(
            bdd_item[Constants.BDD_COL_TABLE_ID]
        )
        table_version = csv_item.get(
            Constants.CSV_COL_VERSION,
            Constants.LATEST_PATH
        )
        table_rom = csv_item.get(
            Constants.CSV_COL_ROM,
            ListHelper.format_value(bdd_item[Constants.BDD_COL_TABLE_ROM])
        )

        # Delete table and its rom
        if Component.EMULATOR_TABLE in Context.get_selected_components():
            if BddHelper.is_not_null_dict_value(
                row=bdd_item,
                column_id=Constants.BDD_COL_TABLE_ROM
            ):

                emulator_path = Context.get_emulator_path(
                    Context.get_selected_emulator()
                )
                relative_paths = self.__list_tables_relative_paths(
                    folder_path=emulator_path,
                    table_id=table_id
                )
                for relative_path in relative_paths:
                    FileHelper.delete_file(
                        file_path=os.path.join(
                            emulator_path,
                            relative_path
                        )
                    )

                relative_paths = FileHelper.list_relative_paths(
                    folder_path=Context.get_emulator_path(
                        Context.get_selected_emulator()
                    ),
                    file_name=bdd_item[Constants.BDD_COL_TABLE_ROM],
                    error_if_not_found=False
                )
                for relative_path in relative_paths:
                    FileHelper.delete_file(
                        file_path=os.path.join(
                            Context.get_emulator_path(
                                Context.get_selected_emulator()
                            ),
                            relative_path
                        )
                    )

            BddHelper.delete_table(
                bdd_file_path=Context.get_pinup_bdd_path(),
                table=bdd_item
            )

        # Delete XML config
        xml_config_path = self.__get_xml_config_path()
        if Component.CONFIG_XML in Context.get_selected_components() and \
                Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X and \
                xml_config_path is not None and \
                xml_config_path.exists():

            XmlHelper.delete_tags(
                xml_file_path=xml_config_path,
                tags=[table_rom]
            )

        # Delete Regedit config
        reg_file_path = self.__get_data_reg_file_path(
            table_id=table_id,
            table_version=table_version
        )
        if Component.CONFIG_REG in Context.get_selected_components() and \
                Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X and \
                reg_file_path is not None and \
                reg_file_path.exists():

            WinRegHelper.delete_user_key(
                key=f'{Constants.VPINMAME_REG_KEY}\\{table_rom}'
            )

        # Delete pup videos
        if Component.PINUP_VIDEOS in Context.get_selected_components() and \
            BddHelper.is_not_null_dict_value(
            row=bdd_item,
            column_id=Constants.BDD_COL_VIDEOS_PATH
        ):

            source_videos_folder_path = self.__get_pinup_videos_path(
                table_videos_path=bdd_item[Constants.BDD_COL_VIDEOS_PATH]
            )
            FileHelper.delete_folder(
                folder_path=source_videos_folder_path
            )

        # Delete media files
        if Component.PINUP_MEDIA in Context.get_selected_components():

            relative_paths = self.__list_tables_relative_paths(
                folder_path=Context.get_pinup_media_path(),
                table_id=table_id
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

        # Retrieve table's data
        table_id = csv_item[Constants.CSV_COL_ID]
        table_version = csv_item[Constants.CSV_COL_VERSION]

        # Insert table and its rom
        if Component.EMULATOR_TABLE in Context.get_selected_components():
            source_folder_path = self.__get_data_emulator_path(
                table_id=table_id,
                table_version=table_version
            )
            destination_folder_path = Context.get_emulator_path(
                Context.get_selected_emulator()
            )
            relative_paths = FileHelper.list_relative_paths(
                folder_path=source_folder_path,
                file_name='*',
                error_if_not_found=False
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

            BddHelper.insert_table(
                bdd_file_path=Context.get_pinup_bdd_path(),
                table_data=csv_item,
                emulator=Context.get_selected_emulator()
            )

        # Insert XML config
        xml_config_path = self.__get_xml_config_path()
        if Component.CONFIG_XML in Context.get_selected_components() and \
                Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X and \
                xml_config_path is not None and \
                xml_config_path.exists():

            XmlHelper.import_tags(
                xml_file_path=xml_config_path,
                extracted_file_path=self.__get_data_xml_config_path(
                    table_id=table_id,
                    table_version=table_version
                ),
                parent_tag='B2STableSettings'
            )

        # Insert Regedit config
        reg_file_path = self.__get_data_reg_file_path(
            table_id=table_id,
            table_version=table_version
        )
        if Component.CONFIG_REG in Context.get_selected_components() and \
                Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X and \
                reg_file_path is not None and \
                reg_file_path.exists():

            WinRegHelper.import_user_key(
                extracted_file_path=reg_file_path
            )

        # Insert pup videos
        if Component.PINUP_VIDEOS in Context.get_selected_components() and \
            BddHelper.is_not_null_dict_value(
            row=csv_item,
            column_id=Constants.CSV_COL_VIDEOS_PATH
        ):

            videos_path = csv_item[Constants.CSV_COL_VIDEOS_PATH]
            source_folder_path = self.__get_data_pinup_videos_path(
                table_id=table_id,
                table_version=table_version,
                table_videos_path=videos_path
            )
            destination_folder_path = self.__get_pinup_videos_path(
                table_videos_path=videos_path
            )
            relative_paths = FileHelper.list_relative_paths(
                folder_path=source_folder_path,
                file_name='*'
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

        # Insert media files
        if Component.PINUP_MEDIA in Context.get_selected_components():

            source_folder_path = self.__get_data_media_path(
                table_id=table_id,
                table_version=table_version
            )
            destination_folder_path = Context.get_pinup_media_path()
            relative_paths = self.__list_tables_relative_paths(
                folder_path=source_folder_path,
                table_id=table_id
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
        bdd_item: dict,
        csv_item: dict
    ):
        """Execute export"""

        if bdd_item is None:
            return

        # Retrieve table's data
        table_id = ListHelper.format_value(
            bdd_item[Constants.BDD_COL_TABLE_ID]
        )
        table_file_path = bdd_item[Constants.BDD_COL_TABLE_GAME_FILE]
        table_file_name = os.path.splitext(table_file_path)[0]
        table_file_extension = os.path.splitext(table_file_path)[1]
        table_version = csv_item.get(
            Constants.CSV_COL_VERSION,
            Constants.LATEST_PATH
        )
        table_available = csv_item.get(
            Constants.CSV_COL_AVAILABLE,
            Constants.CSV_YES_VALUE
        )
        table_weblink_url = csv_item.get(
            Constants.CSV_COL_WEBLINK_URL,
            None
        )
        table_weblink2_url = csv_item.get(
            Constants.CSV_COL_WEBLINK2_URL,
            None
        )
        table_name = csv_item.get(
            Constants.CSV_COL_NAME,
            ListHelper.format_value(bdd_item[Constants.BDD_COL_TABLE_NAME])
        )
        table_alt_exe = csv_item.get(
            Constants.CSV_COL_ALT_EXE,
            ListHelper.format_value(bdd_item['ALTEXE'])
        )
        table_alt_run_mode = csv_item.get(
            Constants.CSV_COL_ALT_RUN_MODE,
            ListHelper.format_value(bdd_item['AltRunMode'])
        )
        table_rom = csv_item.get(
            Constants.CSV_COL_ROM,
            ListHelper.format_value(bdd_item['ROM'])
        )
        videos_path = csv_item.get(
            Constants.CSV_COL_VIDEOS_PATH, None
        )

        match Context.get_selected_emulator():
            case Emulator.VISUAL_PINBALL_X:

                # Export table and its rom
                if Component.EMULATOR_TABLE in Context.get_selected_components():

                    # Set specific alt exe
                    table_alt_exe = csv_item.get(
                        Constants.CSV_COL_ALT_EXE,
                        'VPinballX10_7_3_32bit.exe'
                    )

                    # Extract emulator if not already extracted
                    source_folder_path = Context.get_emulator_path(
                        Context.get_selected_emulator()
                    )
                    destination_folder_path = self.__get_data_emulator_path(
                        table_id=table_id,
                        table_version=table_version
                    )
                    relative_paths = self.__list_tables_relative_paths(
                        folder_path=source_folder_path,
                        table_id=table_file_name
                    )
                    for relative_path in relative_paths:
                        destination_file_path = os.path.join(
                            destination_folder_path,
                            relative_path
                        )
                        destination_file_path = destination_file_path.replace(
                            table_file_name,
                            table_id
                        )
                        copy_result = FileHelper.copy_file(
                            source_file_path=os.path.join(
                                source_folder_path,
                                relative_path
                            ),
                            destination_file_path=destination_file_path
                        )

                        # Generate a script file for Visual Pinball X
                        if copy_result and \
                                videos_path is None and \
                                relative_path.endswith(table_file_path):
                            cmd = self.__get_extract_cmd(
                                table_alt_exe=table_alt_exe)
                            cmd += ' "'
                            cmd += destination_file_path
                            cmd += '"'
                            CmdHelper.run(cmd)

                        # Extract pup videos and specific data
                        if relative_path.endswith(table_file_path):
                            if videos_path is None:
                                # Extract videos path and rom from the script
                                file_content = FileHelper.read_file(
                                    file_path=destination_file_path.replace(
                                        table_file_extension,
                                        '.vbs'
                                    )
                                )

                                # Extract cPuPPack
                                pattern_cpuppack = r'cPuPPack\s*=\s*"\s*([^"]+)\s*"'
                                match_cpuppack = re.search(
                                    pattern_cpuppack, file_content)
                                if match_cpuppack:
                                    videos_path = match_cpuppack.group(1)

                                # Extract cGameName
                                pattern_cgamename = r'cGameName\s*=\s*"\s*([^"]+)\s*"'
                                match_cgamename = re.search(
                                    pattern_cgamename, file_content)
                                if match_cgamename:
                                    table_rom = match_cgamename.group(1)
                                    if videos_path is None:
                                        videos_path = table_rom

                            # Extract rom files
                            rom_relative_paths = []
                            if table_rom is not None:
                                source_rom_folder_path = Context.get_emulator_path(
                                    Context.get_selected_emulator()
                                )
                                rom_relative_paths = FileHelper.list_relative_paths(
                                    folder_path=source_rom_folder_path,
                                    file_name=table_rom,
                                    error_if_not_found=False
                                )
                            if len(rom_relative_paths) == 0:
                                table_rom = None
                            else:
                                destination_rom_folder_path = self.__get_data_emulator_path(
                                    table_id=table_id,
                                    table_version=table_version
                                )
                                for rom_relative_path in rom_relative_paths:
                                    FileHelper.copy_file(
                                        source_file_path=os.path.join(
                                            source_rom_folder_path,
                                            rom_relative_path
                                        ),
                                        destination_file_path=os.path.join(
                                            destination_rom_folder_path,
                                            rom_relative_path
                                        )
                                    )

                # Export XML config
                if Component.CONFIG_XML in Context.get_selected_components() and \
                        table_rom is not None:

                    XmlHelper.extract_tags(
                        xml_file_path=self.__get_xml_config_path(),
                        extracted_file_path=self.__get_data_xml_config_path(
                            table_id=table_id,
                            table_version=table_version
                        ),
                        tags=[table_rom]
                    )

                # Export Regedit config
                if Component.CONFIG_REG in Context.get_selected_components() and \
                        table_rom is not None:

                    WinRegHelper.extract_user_key(
                        extracted_file_path=self.__get_data_reg_file_path(
                            table_id=table_id,
                            table_version=table_version
                        ),
                        key=f'{Constants.VPINMAME_REG_KEY}\\{table_rom}'
                    )

            case Emulator.PINBALL_FX2:

                # Set videos path
                if videos_path is None:
                    videos_path = table_id

            case Emulator.PINBALL_FX3:

                # Set videos path
                if videos_path is None:
                    videos_path = table_id

            case Emulator.PINBALL_FX:

                # Extract emulator if not already extracted
                source_folder_path = Context.get_emulator_path(
                    Context.get_selected_emulator()
                )
                destination_folder_path = self.__get_data_emulator_path(
                    table_id=table_id,
                    table_version=table_version
                )
                relative_paths = self.__list_tables_relative_paths(
                    folder_path=source_folder_path,
                    table_id=table_id
                )
                for relative_path in relative_paths:
                    destination_file_path = os.path.join(
                        destination_folder_path,
                        relative_path
                    )
                    destination_file_path = destination_file_path.replace(
                        table_file_name, table_id)
                    copy_result = FileHelper.copy_file(
                        source_file_path=os.path.join(
                            source_folder_path,
                            relative_path
                        ),
                        destination_file_path=destination_file_path
                    )

                # Set videos path
                if videos_path is None:
                    videos_path = table_id

            case Emulator.PINBALL_M:

                # Set videos path
                if videos_path is None:
                    videos_path = table_id

            case Emulator.FUTURE_PINBALL:

                # Set videos path
                if videos_path is None:
                    videos_path = table_id

                # Export table and its rom
                if Component.EMULATOR_TABLE in Context.get_selected_components():

                    # Extract emulator if not already extracted
                    source_folder_path = Context.get_emulator_path(
                        Context.get_selected_emulator()
                    )
                    destination_folder_path = self.__get_data_emulator_path(
                        table_id=table_id,
                        table_version=table_version
                    )
                    relative_paths = self.__list_tables_relative_paths(
                        folder_path=source_folder_path,
                        table_id=table_file_name
                    )
                    for relative_path in relative_paths:
                        destination_file_path = os.path.join(
                            destination_folder_path,
                            relative_path
                        )
                        destination_file_path = destination_file_path.replace(
                            table_file_name,
                            table_id
                        )
                        copy_result = FileHelper.copy_file(
                            source_file_path=os.path.join(
                                source_folder_path,
                                relative_path
                            ),
                            destination_file_path=destination_file_path
                        )

            case _:
                raise Exception(Context.get_text(
                    'error_emulator_not_implemented',
                    emulator=Context.get_selected_emulator().value
                ))

        # Export pup videos
        if Component.PINUP_VIDEOS in Context.get_selected_components():

            videos_relative_paths = []
            if videos_path is not None:
                source_videos_folder_path = self.__get_pinup_videos_path(
                    table_videos_path=videos_path
                )
                videos_relative_paths = FileHelper.list_relative_paths(
                    folder_path=source_videos_folder_path,
                    file_name='*',
                    error_if_not_found=False
                )
            if len(videos_relative_paths) == 0:
                videos_path = None
            else:
                destination_videos_folder_path = self.__get_data_pinup_videos_path(
                    table_id=table_id,
                    table_version=table_version,
                    table_videos_path=videos_path
                )
                for videos_relative_path in videos_relative_paths:
                    FileHelper.copy_file(
                        source_file_path=os.path.join(
                            source_videos_folder_path,
                            videos_relative_path
                        ),
                        destination_file_path=os.path.join(
                            destination_videos_folder_path,
                            videos_relative_path
                        )
                    )

        # Export media files
        if Component.PINUP_MEDIA in Context.get_selected_components():

            source_folder_path = Context.get_pinup_media_path()
            destination_folder_path = self.__get_data_media_path(
                table_id=table_id,
                table_version=table_version
            )
            relative_paths = self.__list_tables_relative_paths(
                folder_path=source_folder_path,
                table_id=table_file_name
            )
            for relative_path in relative_paths:
                destination_file_path = os.path.join(
                    destination_folder_path,
                    relative_path
                )
                destination_file_path = destination_file_path.replace(
                    table_file_name, table_id)
                FileHelper.copy_file(
                    source_file_path=os.path.join(
                        source_folder_path,
                        relative_path
                    ),
                    destination_file_path=destination_file_path
                )

        # Write data in CSV
        csv_tables = ListHelper.replace_item(
            a_list=CsvHelper.read_data(
                file_path=Context.get_csv_path()
            ),
            item={
                Constants.CSV_COL_AVAILABLE: table_available,
                Constants.CSV_COL_VERSION: table_version,
                Constants.CSV_COL_NAME: table_name,
                Constants.CSV_COL_ID: table_id,
                Constants.CSV_COL_ALT_EXE: table_alt_exe,
                Constants.CSV_COL_ALT_RUN_MODE: table_alt_run_mode,
                Constants.CSV_COL_ROM: table_rom,
                Constants.CSV_COL_VIDEOS_PATH: videos_path,
                Constants.CSV_COL_WEBLINK_URL: table_weblink_url,
                Constants.CSV_COL_WEBLINK2_URL: table_weblink2_url
            },
            id_column=Constants.CSV_COL_ID
        )
        CsvHelper.write_data(
            file_path=Context.get_csv_path(),
            data=csv_tables
        )

    def __execute_copy(
        self,
        csv_item: dict
    ):
        """Execute copy"""

        if csv_item is None:
            return

        # Retrieve table's data
        table_id = csv_item[Constants.CSV_COL_ID]
        table_version = csv_item[Constants.CSV_COL_VERSION]

        # Copy table and its rom
        if Component.EMULATOR_TABLE in Context.get_selected_components():

            # Copy item in a CSV file
            CsvHelper.write_data(
                file_path=os.path.join(
                    self.get_copy_folder_path(),
                    table_id,
                    'database.csv'
                ),
                data=[csv_item]
            )

            # Copy files for tables
            source_folder_path = self.__get_data_emulator_path(
                table_id=table_id,
                table_version=table_version
            )
            destination_folder_path = os.path.join(
                self.get_copy_folder_path(),
                table_id,
                'emulator'
            )
            FileHelper.copy_folder(
                source_folder_path=source_folder_path,
                destination_folder_path=destination_folder_path
            )

        # Copy XML config
        xml_config_path = self.__get_data_xml_config_path(
            table_id=table_id,
            table_version=table_version
        )
        if Component.CONFIG_XML in Context.get_selected_components() and \
                Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X and \
                xml_config_path is not None and \
                xml_config_path.exists():

            destination_file_path = os.path.join(
                self.get_copy_folder_path(),
                table_id,
                'config',
                'B2STableSettings.xml'
            )
            FileHelper.copy_file(
                source_file_path=xml_config_path,
                destination_file_path=destination_file_path
            )

        # Copy Regedit config
        reg_file_path = self.__get_data_reg_file_path(
            table_id=table_id,
            table_version=table_version
        )
        if Component.CONFIG_REG in Context.get_selected_components() and \
                Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X and \
                reg_file_path is not None and \
                reg_file_path.exists():

            destination_file_path = os.path.join(
                self.get_copy_folder_path(),
                table_id,
                'config',
                f'user_values{Constants.REGEDIT_FILE_EXTENSION}'
            )
            FileHelper.copy_file(
                source_file_path=reg_file_path,
                destination_file_path=destination_file_path
            )

        # Copy pup videos
        if Component.PINUP_VIDEOS in Context.get_selected_components() and \
            BddHelper.is_not_null_dict_value(
            row=csv_item,
            column_id=Constants.CSV_COL_VIDEOS_PATH
        ):

            videos_path = csv_item[Constants.CSV_COL_VIDEOS_PATH]
            source_folder_path = self.__get_data_pinup_videos_path(
                table_id=table_id,
                table_version=table_version,
                table_videos_path=videos_path
            )
            destination_folder_path = os.path.join(
                self.get_copy_folder_path(),
                table_id,
                'PUPVideos'
            )
            FileHelper.copy_folder(
                source_folder_path=source_folder_path,
                destination_folder_path=destination_folder_path
            )

        # Copy media files
        if Component.PINUP_MEDIA in Context.get_selected_components():

            source_folder_path = self.__get_data_media_path(
                table_id=table_id,
                table_version=table_version
            )
            destination_folder_path = os.path.join(
                self.get_copy_folder_path(),
                table_id,
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
        bdd_item = BddHelper.get_table(
            bdd_file_path=Context.get_pinup_bdd_path(),
            emulator=Context.get_selected_emulator(),
            table_id=item_id
        )

        match(Context.get_selected_action()):
            case Action.UNINSTALL:
                self.__execute_uninstall(
                    bdd_item=bdd_item,
                    csv_item=csv_item
                )

            case Action.INSTALL:
                self.__execute_uninstall(
                    bdd_item=bdd_item,
                    csv_item=csv_item
                )
                self.__execute_install(
                    csv_item=csv_item
                )

            case Action.EXPORT:
                self.__execute_export(
                    bdd_item=bdd_item,
                    csv_item=csv_item
                )

            case Action.COPY:
                self.__execute_copy(
                    csv_item=csv_item
                )
