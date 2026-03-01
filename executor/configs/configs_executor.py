#!/usr/bin/python3
"""Executor to manage Configs"""


import os
from executor.abstract_executor import AbstractExecutor
from libraries.constants.constants import Action, Component, Constants
from libraries.context.context import Context
from libraries.file.file_helper import FileHelper
from libraries.winreg.winreg_helper import WinRegHelper


class ConfigsExecutor(AbstractExecutor):
    """Executor to manage Configs"""

    def __execute_uninstall(
        self,
        config: str
    ):
        """Execute uninstall"""

        # Uninstall FILES
        if Component.FILES in Context.get_selected_components():
            config_path = os.path.join(
                Context.get_configs_path(),
                config,
                Component.FILES.name.lower()
            )
            for relative_path in FileHelper.list_relative_paths(
                folder_path=config_path,
                file_name='*',
                error_if_not_found=False
            ):
                FileHelper.delete_file(
                    file_path=os.path.join(
                        str(Context.get_pinup_path().drive) + '\\',
                        relative_path
                    )
                )

        # Uninstall REGISTRY
        if Component.REGISTRY in Context.get_selected_components():
            config_path = os.path.join(
                Context.get_configs_path(),
                config,
                Component.REGISTRY.name.lower()
            )
            for relative_path in FileHelper.list_relative_paths(
                folder_path=config_path,
                file_name='*',
                error_if_not_found=False
            ):
                for key in WinRegHelper.extract_regedit_keys(
                    file_path=os.path.join(
                        config_path,
                        relative_path
                    )
                ):
                    if not key.startswith(Constants.REGEDIT_ROOT_KEY_NAME):
                        continue

                    WinRegHelper.delete_user_key(
                        key=key[len(Constants.REGEDIT_ROOT_KEY_NAME) + 1:]
                    )

    def __execute_install(
        self,
        config: str
    ):
        """Execute install"""

        # Install FILES
        if Component.FILES in Context.get_selected_components():
            config_path = os.path.join(
                Context.get_configs_path(),
                config,
                Component.FILES.name.lower()
            )
            for relative_path in FileHelper.list_relative_paths(
                folder_path=config_path,
                file_name='*',
                error_if_not_found=False
            ):
                FileHelper.copy_file(
                    source_file_path=os.path.join(
                        config_path,
                        relative_path
                    ),
                    destination_file_path=os.path.join(
                        str(Context.get_pinup_path().drive) + '\\',
                        relative_path
                    )
                )

        # Install REGISTRY
        if Component.REGISTRY in Context.get_selected_components():
            config_path = os.path.join(
                Context.get_configs_path(),
                config,
                Component.REGISTRY.name.lower()
            )
            for relative_path in FileHelper.list_relative_paths(
                folder_path=config_path,
                file_name='*',
                error_if_not_found=False
            ):
                WinRegHelper.import_user_key(
                    extracted_file_path=os.path.join(
                        config_path,
                        relative_path
                    )
                )

    def __execute_export(
        self,
        config: str
    ):
        """Execute export"""

        # Export FILES
        if Component.FILES in Context.get_selected_components():
            config_path = os.path.join(
                Context.get_configs_path(),
                config,
                Component.FILES.name.lower()
            )
            for relative_path in FileHelper.list_relative_paths(
                folder_path=config_path,
                file_name='*',
                error_if_not_found=False
            ):
                FileHelper.copy_file(
                    source_file_path=os.path.join(
                        str(Context.get_pinup_path().drive) + '\\',
                        relative_path
                    ),
                    destination_file_path=os.path.join(
                        config_path,
                        relative_path
                    )
                )

        # Export REGISTRY
        if Component.REGISTRY in Context.get_selected_components():
            config_path = os.path.join(
                Context.get_configs_path(),
                config,
                Component.REGISTRY.name.lower()
            )
            for relative_path in FileHelper.list_relative_paths(
                folder_path=config_path,
                file_name='*',
                error_if_not_found=False
            ):
                regedit_file_path = os.path.join(
                    config_path,
                    relative_path
                )
                for key in WinRegHelper.extract_regedit_keys(
                    file_path=regedit_file_path
                ):
                    if not key.startswith(Constants.REGEDIT_ROOT_KEY_NAME):
                        continue

                    WinRegHelper.extract_user_key(
                        extracted_file_path=regedit_file_path,
                        key=key[len(Constants.REGEDIT_ROOT_KEY_NAME) + 1:]
                    )

    def do_execution(self, item_id: str):
        """Do execution for an item"""

        match(Context.get_selected_action()):

            case Action.UNINSTALL:
                self.__execute_uninstall(
                    config=item_id
                )

            case Action.INSTALL:
                self.__execute_uninstall(
                    config=item_id
                )
                self.__execute_install(
                    config=item_id
                )

            case Action.EXPORT:
                self.__execute_export(
                    config=item_id
                )
