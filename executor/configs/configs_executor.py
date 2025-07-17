#!/usr/bin/python3
"""Executor to manage Configs"""


import os
from executor.abstract_executor import AbstractExecutor
from libraries.constants.constants import Action
from libraries.context.context import Context
from libraries.file.file_helper import FileHelper


class ConfigsExecutor(AbstractExecutor):
    """Executor to manage Configs"""

    def __execute_uninstall(
        self,
        config_text: str
    ):
        """Execute uninstall"""

        for source_folder_path in Context.get_config_paths(
            components=Context.get_selected_components(),
            config_text=config_text
        ):
            relative_paths = FileHelper.list_relative_paths(
                folder_path=source_folder_path,
                file_name='*',
                error_if_not_found=False
            )
            for relative_path in relative_paths:
                FileHelper.delete_file(
                    file_path=os.path.join(
                        str(Context.get_pinup_path().drive) + '\\',
                        relative_path
                    )
                )

    def __execute_install(
        self,
        config_text: str
    ):
        """Execute install"""

        for source_folder_path in Context.get_config_paths(
            components=Context.get_selected_components(),
            config_text=config_text
        ):
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
                        str(Context.get_pinup_path().drive) + '\\',
                        relative_path
                    )
                )

    def __execute_export(
        self,
        config_text: str
    ):
        """Execute export"""

        for source_folder_path in Context.get_config_paths(
            components=Context.get_selected_components(),
            config_text=config_text
        ):
            relative_paths = FileHelper.list_relative_paths(
                folder_path=source_folder_path,
                file_name='*',
                error_if_not_found=False
            )
            for relative_path in relative_paths:
                FileHelper.copy_file(
                    source_file_path=os.path.join(
                        str(Context.get_pinup_path().drive) + '\\',
                        relative_path
                    ),
                    destination_file_path=os.path.join(
                        source_folder_path,
                        relative_path
                    )
                )

    def do_execution(self, item_id: str):
        """Do execution for an item"""

        match(Context.get_selected_action()):

            case Action.UNINSTALL:
                self.__execute_uninstall(
                    config_text=item_id
                )

            case Action.INSTALL:
                self.__execute_uninstall(
                    config_text=item_id
                )
                self.__execute_install(
                    config_text=item_id
                )

            case Action.EXPORT:
                self.__execute_export(
                    config_text=item_id
                )
