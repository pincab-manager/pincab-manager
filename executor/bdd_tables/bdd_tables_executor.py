#!/usr/bin/python3
"""Executor to manage BDD Tables"""


import os
from pathlib import Path
from executor.abstract_executor import AbstractExecutor
from libraries.constants.constants import Action, Component, Constants
from libraries.context.context import Context
from libraries.csv.csv_helper import CsvHelper
from libraries.bdd.bdd_helper import BddHelper
from libraries.file.file_helper import FileHelper


class BDDTablesExecutor(AbstractExecutor):
    """Executor to manage BDD Tables"""

    def __get_csv_path(
        self,
        bdd_table_name: str
    ):
        """Get CSV path"""

        return Path(os.path.join(
            Context.get_bdd_path(),
            Constants.COMMON_PATH,
            f'bdd_table_{bdd_table_name.lower()}.csv'
        ))

    def __get_emulator_script_path(
        self,
        emulator_id: str,
        script_name: str
    ):
        """Get emulator script path"""
        emulator_name = None
        for emulator, current_id in Constants.EMULATORS_IDS.items():
            if str(current_id) == str(emulator_id):
                emulator_name = emulator.value

        return os.path.join(
            Context.get_bdd_path(),
            emulator_name,
            f'{script_name}.txt'
        )

    def __get_common_script_path(
        self,
        script_name: str
    ):
        """Get common script path"""
        return os.path.join(
            Context.get_bdd_path(),
            Constants.COMMON_PATH,
            f'{script_name}.txt'
        )

    def __list_emulator_script_names(self):
        """List emulator script names"""
        return ['LaunchScript', 'PostScript']

    def __list_common_script_names(self):
        """List common script names"""
        return ['GlobalOptions']

    def __execute_uninstall(
        self,
        bdd_table_name: str
    ):
        """Execute uninstall"""

        # Uninstall BDD Tables
        if Component.PINUP_DATABASE in Context.get_selected_components():

            BddHelper.delete_items(
                bdd_file_path=Context.get_pinup_bdd_path(),
                bdd_table_name=bdd_table_name
            )

    def __execute_install(
        self,
        bdd_table_name: str
    ):
        """Execute install"""

        # Install BDD Tables
        if Component.PINUP_DATABASE in Context.get_selected_components():

            data = CsvHelper.read_data(
                file_path=self.__get_csv_path(
                    bdd_table_name=bdd_table_name
                )
            )

            # Retrieve items from data
            items = []
            for item in data:
                # Extract scripts from file
                for key in item.keys():
                    if key in self.__list_emulator_script_names():
                        file_path = self.__get_emulator_script_path(
                            emulator_id=int(item['EMUID']),
                            script_name=key
                        )
                        content = FileHelper.read_file(
                            file_path=file_path
                        )
                        item[key] = content
                    elif key in self.__list_common_script_names():
                        file_path = self.__get_common_script_path(
                            script_name=key
                        )
                        content = FileHelper.read_file(
                            file_path=file_path
                        )
                        item[key] = content
                    else:
                        item[key] = BddHelper.format_value(
                            value=item[key]
                        )

                # Append item
                items.append(item)

            # Insert data
            BddHelper.insert_items(
                bdd_file_path=Context.get_pinup_bdd_path(),
                bdd_table_name=bdd_table_name,
                items=items
            )

    def __execute_export(
        self,
        bdd_table_name: str
    ):
        """Execute export"""

        # Export BDD Tables
        if Component.PINUP_DATABASE in Context.get_selected_components():

            # Retrieve data from items
            data = []
            for item in BddHelper.list_items(
                bdd_file_path=Context.get_pinup_bdd_path(),
                table_name=bdd_table_name
            ):
                # Ignore item if not visible
                if 'Visible' in item and item['Visible'] == 0:
                    continue

                # Extract scripts from item
                for key in item.keys():
                    if key in self.__list_emulator_script_names():
                        file_path = self.__get_emulator_script_path(
                            emulator_id=item['EMUID'],
                            script_name=key
                        )
                        FileHelper.write_file(
                            file_path=file_path,
                            content=item[key]
                        )
                        item[key] = key
                    elif key in self.__list_common_script_names():
                        file_path = self.__get_common_script_path(
                            script_name=key
                        )
                        FileHelper.write_file(
                            file_path=file_path,
                            content=item[key]
                        )
                        item[key] = key

                # Append item
                data.append(item)

            # Export in a CSV file the config table
            CsvHelper.write_data(
                file_path=self.__get_csv_path(
                    bdd_table_name=bdd_table_name
                ),
                data=data,
                sort_column_id=''
            )

    def do_execution(self, item_id: str):
        """Do execution for an item"""

        match(Context.get_selected_action()):

            case Action.UNINSTALL:
                self.__execute_uninstall(
                    bdd_table_name=item_id
                )

            case Action.INSTALL:
                self.__execute_uninstall(
                    bdd_table_name=item_id
                )
                self.__execute_install(
                    bdd_table_name=item_id
                )

            case Action.EXPORT:
                self.__execute_export(
                    bdd_table_name=item_id
                )
