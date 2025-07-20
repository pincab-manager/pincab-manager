#!/usr/bin/python3
"""Windows Registry Helper"""

import re
import os
import winreg
import subprocess
from libraries.constants.constants import Constants
from libraries.context.context import Context
from libraries.file.file_helper import FileHelper
from libraries.logging.logging_helper import LoggingHelper


class WinRegHelper:
    """Class to help usage of Windows Registry"""

    @staticmethod
    def __convert_value_to_reg_format(name, value, value_type):
        """Convert values for registry"""
        if value_type == winreg.REG_DWORD:
            return f'"{name}"=dword:{value:08x}'
        if value_type == winreg.REG_BINARY:
            value_hex = ",".join([f'{b:02x}' for b in value])
            return f'"{name}"=hex:{value_hex}'
        return f'Unknown type for {name}'

    @staticmethod
    def __load_values_from_reg_file(
        file_path: str
    ):
        """
        Parses a .reg file to extract the key path and its values (only REG_DWORD supported).

        :param file_path: Path to the .reg file
        :return: Tuple (registry key path, dict of value_name -> (type, value))
        """
        values = {}

        file_content = FileHelper.read_file(
            file_path=file_path,
            encoding=Constants.REGEDIT_FILE_ENCODING
        )
        registry_path = None
        for line in file_content.splitlines():
            line = line.strip()
            # Detect the registry key path in [brackets]
            if line.startswith('[') and line.endswith(']'):
                registry_path = line[1:-1]
            # Parse lines of the form "name"=dword:00000001
            elif '=' in line:
                match = re.match(
                    r'"(.+?)"=(dword|hex|hex\(.*?\)|".*?")(.+)',
                    line
                )
                if match:
                    name, value_type, raw_data = match.groups()
                    value_type = value_type.lower()
                    raw_data = raw_data.strip()

                    # Handle REG_DWORD values
                    if value_type.startswith("dword"):
                        value = int(raw_data.split(':')[-1], 16)
                        values[name] = ("REG_DWORD", value)

                    # Other types can be added here if needed

        return registry_path, values

    @staticmethod
    def __open_key_from_path(
        full_path: str
    ):
        """
        Splits a full registry path and opens the key using winreg.

        :param full_path: Full registry path (e.g., HKEY_CURRENT_USER\\Software\\...)
        :return: Opened key handle
        """
        root_keys = {
            "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
            "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
            "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
            "HKEY_USERS": winreg.HKEY_USERS,
            "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG,
        }

        parts = full_path.split("\\", 1)
        root_name, sub_key = parts[0], parts[1]
        root = root_keys.get(root_name.upper())

        if root is None:
            raise ValueError(f"Unknown root key: {root_name}")

        return winreg.OpenKey(root, sub_key)

    @staticmethod
    def __load_values_from_registry(
        full_path: str
    ):
        """
        Loads all values from a registry key using winreg (supports REG_DWORD).

        :param full_path: Full registry path
        :return: Dictionary of value_name -> (type, value)
        """
        values = {}
        with WinRegHelper.__open_key_from_path(full_path) as key:
            i = 0
            while True:
                try:
                    name, val, val_type = winreg.EnumValue(key, i)
                    type_str = {
                        winreg.REG_DWORD: "REG_DWORD"
                    }.get(val_type)
                    if type_str:
                        values[name] = (type_str, val)
                    i += 1
                except OSError:
                    break
        return values

    @staticmethod
    def is_user_key_exists(
        key: str
    ):
        """Specify if user key exists"""

        try:
            winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key,
                0,
                winreg.KEY_READ
            )
            return True
        except Exception as exc:
            LoggingHelper.log_error(
                message=Context.get_text(
                    'error_unknown'
                ),
                exc=exc
            )
            return False

    @staticmethod
    def extract_user_key(
        extracted_file_path: str,
        key: str
    ):
        """Extract user key"""

        export_content = ''
        try:
            # Open the registry key
            registry_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key,
                0,
                winreg.KEY_READ
            )

            # Read all values from the key
            i = 0
            while True:
                try:
                    if len(export_content) == 0:
                        # Header for reg
                        export_content += "Windows Registry Editor Version 5.00\n\n"

                        # Add key
                        export_content += f"[{Constants.REGEDIT_ROOT_KEY_NAME}\\{key}]\n"

                    name, value, value_type = winreg.EnumValue(registry_key, i)
                    export_content += WinRegHelper.__convert_value_to_reg_format(
                        name, value, value_type) + "\n"
                    i += 1
                except OSError as exc:
                    LoggingHelper.log_error(
                        message=Context.get_text(
                            'error_unknown'
                        ),
                        exc=exc
                    )
                    break

            winreg.CloseKey(registry_key)
        except WindowsError as exc:
            LoggingHelper.log_error(
                message=Context.get_text(
                    'error_unknown'
                ),
                exc=exc
            )
            return

        if len(export_content) == 0:
            return

        if Context.is_simulated():
            LoggingHelper.log_info(
                message=Context.get_text(
                    'extract_user_key_simulation',
                    file=str(extracted_file_path)
                )
            )
            return

        LoggingHelper.log_info(
            message=Context.get_text(
                'extract_user_key_in_progress',
                file=str(extracted_file_path)
            )
        )
        os.makedirs(os.path.dirname(extracted_file_path), exist_ok=True)
        FileHelper.write_file(
            file_path=extracted_file_path,
            content=export_content,
            encoding=Constants.REGEDIT_FILE_ENCODING
        )

    @staticmethod
    def delete_user_key(
        key: str
    ):
        """Delete user key"""

        if Context.is_simulated():
            LoggingHelper.log_info(
                message=Context.get_text(
                    'delete_user_key_simulation',
                    key=key
                )
            )
            return

        LoggingHelper.log_info(
            message=Context.get_text(
                'delete_user_key_in_progress',
                key=key
            )
        )
        try:
            winreg.DeleteKey(
                winreg.HKEY_CURRENT_USER,
                key
            )
        except Exception as exc:
            LoggingHelper.log_error(
                message=Context.get_text(
                    'error_unknown'
                ),
                exc=exc
            )
            return

    @staticmethod
    def import_user_key(
        extracted_file_path: str
    ):
        """Import user key"""

        if Context.is_simulated():
            LoggingHelper.log_info(
                message=Context.get_text(
                    'import_user_key_simulation',
                    file=str(extracted_file_path)
                )
            )
            return

        LoggingHelper.log_info(
            message=Context.get_text(
                'import_user_key_in_progress',
                file=str(extracted_file_path)
            )
        )

        try:
            subprocess.run(
                ["reg", "import", extracted_file_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as exc:
            LoggingHelper.log_error(
                message=Context.get_text(
                    'error_unknown'
                ),
                exc=exc
            )
            return

    @staticmethod
    def get_user_keys_tree(path="") -> dict:
        """Get all users keys in a tree"""
        tree = {}
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
            # Retrieve sub keys
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    full_path = f"{path}\\{subkey_name}" if path else subkey_name
                    tree[subkey_name] = WinRegHelper.get_user_keys_tree(
                        full_path
                    )
                    i += 1
                except Exception:
                    break  # No more key

        return tree

    @staticmethod
    def extract_regedit_keys(
        file_path: str
    ) -> list[str]:
        """Extract regedit keys from a file"""

        if not file_path.endswith(Constants.REGEDIT_FILE_EXTENSION):
            return None

        result = []

        file_content = FileHelper.read_file(
            file_path=file_path,
            encoding=Constants.REGEDIT_FILE_ENCODING
        )
        for line in file_content.splitlines():
            if line.startswith('[') and line.endswith(']'):
                result.append(line[1:-1])
        return result

    @staticmethod
    def is_reg_file_equal_to_registry(
        file_path: str
    ):
        """
        Compares the values of a registry key defined in a .reg file 
        with the actual values in the Windows Registry.

        :param file_path: Path to the .reg file
        :return: True if values and types match exactly, False otherwise
        """
        reg_path, file_values = WinRegHelper.__load_values_from_reg_file(
            file_path=file_path
        )
        registry_values = WinRegHelper.__load_values_from_registry(
            full_path=reg_path
        )

        match = True

        # pylint: disable=consider-using-dict-items

        # Keys in file but missing or different in registry
        for name in file_values:
            if name not in registry_values:
                LoggingHelper.log_warning(
                    message=Context.get_text(
                        'warning_registry_missing',
                        name=name
                    )
                )
                match = False
            else:
                file_type, file_val = file_values[name]
                reg_type, reg_val = registry_values[name]
                if file_type != reg_type:
                    LoggingHelper.log_warning(
                        message=Context.get_text(
                            'warning_registry_type_mismatch',
                            name=name,
                            file_type=file_type,
                            reg_type=reg_type
                        )
                    )
                    match = False
                elif file_val != reg_val:
                    LoggingHelper.log_warning(
                        message=Context.get_text(
                            'warning_registry_value_mismatch',
                            name=name,
                            file_val=file_val,
                            reg_val=reg_val
                        )
                    )
                    match = False

        # Extra keys in registry not present in the file
        for name in registry_values:
            if name == "":
                continue
            if name not in file_values:
                LoggingHelper.log_warning(
                    message=Context.get_text(
                        'warning_registry_extra',
                        name=name
                    )
                )
                match = False

        return match
