#!/usr/bin/python3
"""Verifier"""

import re
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from libraries.bdd.bdd_helper import BddHelper
from libraries.constants.constants import Constants, Emulator, Component
from libraries.context.context import Context
from libraries.file.file_helper import FileHelper
from libraries.logging.logging_helper import LoggingHelper
from libraries.winreg.winreg_helper import WinRegHelper
from libraries.xml.xml_helper import XmlHelper

# pylint: disable=consider-using-max-builtin, too-many-return-statements
# pylint: disable=too-many-public-methods, too-many-lines


class Verifier:
    """Class to help usage of BDD"""

    @staticmethod
    def verify_none_value(
        value: str
    ):
        """Verify if None value"""

        if value is None:
            return True

        if value == 'None':
            return True

        return False

    @staticmethod
    def verify_csv_bdd_version(
        csv_version: str,
        bdd_version: str
    ):
        """Verify if CSV and BDD are in same version"""

        if Verifier.verify_none_value(csv_version):
            return False

        if Verifier.verify_none_value(bdd_version):
            return False

        return csv_version == bdd_version

    @staticmethod
    def verify_table_versions(
        csv_table_id: str,
        csv_table_weblink_url: str
    ):
        """Verify latest version and unique version for a table"""

        latest_version = None
        unique_version = None

        if Verifier.verify_none_value(csv_table_id):
            return (latest_version, unique_version)

        # Retrieve sub directories to identify if unique version
        sub_directories = FileHelper.list_sub_directories(
            folder_path=os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
                csv_table_id
            )
        )

        unique_version = len(sub_directories) == 1

        # Retrieve version from weblink
        weblink_version = None
        if not Verifier.verify_none_value(csv_table_weblink_url):
            try:
                # If weblink vpuniverse
                if csv_table_weblink_url.startswith('https://vpuniverse.com/'):
                    Context.get_selenium_web_browser().get(csv_table_weblink_url)
                    version_element = WebDriverWait(
                        Context.get_selenium_web_browser(), 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH,
                             "//span[contains(text(), 'Version')]")
                        )
                    )
                    version_element = version_element.text.split(
                        "Version"
                    )[-1].strip()
                    weblink_version = re.sub(r'[^0-9.]', '', version_element)

                # If weblink vpuniverse
                if csv_table_weblink_url.startswith('https://www.vpforums.org/'):
                    Context.get_selenium_web_browser().get(csv_table_weblink_url)
                    title_element = WebDriverWait(
                        Context.get_selenium_web_browser(), 10).until(
                        EC.visibility_of_element_located((By.TAG_NAME, "h1"))
                    )
                    version_element = title_element.text.split()[-1]
                    weblink_version = re.sub(r'[^0-9.]', '', version_element)

                # If weblink pinballnirvana
                if csv_table_weblink_url.startswith('https://pinballnirvana.com/'):
                    Context.get_selenium_web_browser().get(csv_table_weblink_url)
                    title_element = WebDriverWait(
                        Context.get_selenium_web_browser(), 10).until(
                        EC.visibility_of_element_located((By.TAG_NAME, "h1"))
                    )
                    version_element = title_element.text.split()[-1]
                    weblink_version = re.sub(r'[^0-9.]', '', version_element)

            except Exception as exc:
                LoggingHelper.log_error(
                    message=Context.get_text(
                        'error_unknown'
                    ),
                    exc=exc
                )

        if weblink_version is not None:
            latest_version = weblink_version in sub_directories

        return (latest_version, unique_version)

    @staticmethod
    def verify_playlist_version(
        csv_playlist_id: str
    ):
        """Verify latest version for a playlist"""

        if Verifier.verify_none_value(csv_playlist_id):
            return False

        # Retrieve sub directories to identify if unique version
        sub_directories = FileHelper.list_sub_directories(
            folder_path=os.path.join(
                Context.get_working_path(),
                'playlists',
                csv_playlist_id
            )
        )

        return len(sub_directories) == 1

    @staticmethod
    def verify_table_emulator_install(
        bdd_table_id: str,
        bdd_table_version: str
    ):
        """Verify if table install"""

        if Verifier.verify_none_value(bdd_table_id):
            return False

        if Verifier.verify_none_value(bdd_table_version):
            return False

        relative_paths = FileHelper.list_relative_paths(
            folder_path=os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
                bdd_table_id,
                bdd_table_version,
                'emulator'
            ),
            file_name='*',
            error_if_not_found=False
        )

        for relative_path in relative_paths:
            file1_path = os.path.join(
                Context.get_emulator_path(
                    Context.get_selected_emulator()
                ),
                relative_path
            )

            file2_path = os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
                bdd_table_id,
                bdd_table_version,
                'emulator',
                relative_path
            )

            if not FileHelper.is_file_exists(
                file_path=file1_path
            ):
                LoggingHelper.log_warning(
                    message=Context.get_text(
                        'warning_not_found_file',
                        file=str(file1_path)
                    )
                )
                return False

            if not FileHelper.compare_files(
                file1_path=file1_path,
                file2_path=file2_path
            ):
                LoggingHelper.log_warning(
                    message=Context.get_text(
                        'warning_differents_files',
                        file1=str(file1_path),
                        file2=str(file2_path)
                    )
                )
                return False

        return len(relative_paths) > 0

    @staticmethod
    def verify_table_emulator_export(
        bdd_table_id: str,
        bdd_table_version: str,
        csv_table_rom: str
    ):
        """Verify if table export"""

        if Verifier.verify_none_value(bdd_table_id):
            return False

        if Verifier.verify_none_value(bdd_table_version):
            return False

        relative_paths = FileHelper.list_relative_paths(
            folder_path=os.path.join(
                Context.get_emulator_path(
                    Context.get_selected_emulator()
                ),
                'Tables'
            ),
            file_name=f'{bdd_table_id}*',
            error_if_not_found=False
        )

        for relative_path in relative_paths:
            file1_path = os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
                bdd_table_id,
                bdd_table_version,
                'emulator',
                'Tables',
                relative_path
            )

            file2_path = os.path.join(
                Context.get_emulator_path(
                    Context.get_selected_emulator()
                ),
                'Tables',
                relative_path
            )

            if not FileHelper.is_file_exists(
                file_path=file1_path
            ):
                LoggingHelper.log_warning(
                    message=Context.get_text(
                        'warning_not_found_file',
                        file=str(file1_path)
                    )
                )
                return False

            if not FileHelper.compare_files(
                file1_path=file1_path,
                file2_path=file2_path
            ):
                LoggingHelper.log_warning(
                    message=Context.get_text(
                        'warning_differents_files',
                        file1=str(file1_path),
                        file2=str(file2_path)
                    )
                )
                return False

        if Verifier.verify_none_value(csv_table_rom):
            return None

        if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:

            relative_paths = FileHelper.list_relative_paths(
                folder_path=os.path.join(
                    Context.get_emulator_path(
                        Context.get_selected_emulator()
                    ),
                    'VPinMAME'
                ),
                file_name=csv_table_rom,
                error_if_not_found=False
            )

            for relative_path in relative_paths:
                file1_path = os.path.join(
                    Context.get_working_path(),
                    'tables',
                    Context.get_selected_emulator().value,
                    bdd_table_id,
                    bdd_table_version,
                    'emulator',
                    'VPinMAME',
                    relative_path
                )

                file2_path = os.path.join(
                    Context.get_emulator_path(
                        Context.get_selected_emulator()
                    ),
                    'VPinMAME',
                    relative_path
                )

                if not FileHelper.is_file_exists(
                    file_path=file1_path
                ):
                    LoggingHelper.log_warning(
                        message=Context.get_text(
                            'warning_not_found_file',
                            file=str(file1_path)
                        )
                    )
                    return False

                if not FileHelper.compare_files(
                    file1_path=file1_path,
                    file2_path=file2_path
                ):
                    LoggingHelper.log_warning(
                        message=Context.get_text(
                            'warning_differents_files',
                            file1=str(file1_path),
                            file2=str(file2_path)
                        )
                    )
                    return False

        return True

    @staticmethod
    def verify_table_emulator_uninstall(
        bdd_table_id: str,
        bdd_table_version: str
    ):
        """Verify if table vpx uninstall"""

        if Verifier.verify_none_value(bdd_table_id):
            return False

        if Verifier.verify_none_value(bdd_table_version):
            return False

        relative_paths = FileHelper.list_relative_paths(
            folder_path=os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
                bdd_table_id,
                bdd_table_version,
                'emulator'
            ),
            file_name='*',
            error_if_not_found=False
        )

        for relative_path in relative_paths:
            file_path = os.path.join(
                Context.get_emulator_path(
                    Context.get_selected_emulator()
                ),
                relative_path
            )
            if FileHelper.is_file_exists(
                file_path=file_path
            ):
                return False

        return True

    @staticmethod
    def verify_table_pinup_media_install(
        bdd_table_id: str,
        bdd_table_version: str
    ):
        """Verify if table media install"""

        if Verifier.verify_none_value(bdd_table_id):
            return False

        if Verifier.verify_none_value(bdd_table_version):
            return False

        relative_paths = FileHelper.list_relative_paths(
            folder_path=os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
                bdd_table_id,
                bdd_table_version,
                'media'
            ),
            file_name='*',
            error_if_not_found=False
        )

        for relative_path in relative_paths:
            # Ignore cache file
            cache_file_found = False
            for cache_file_name in Constants.CACHE_FILES_NAMES:
                if cache_file_name in relative_path:
                    cache_file_found = True
                    break
            if cache_file_found:
                continue

            file1_path = os.path.join(
                Context.get_pinup_media_path(),
                relative_path
            )

            file2_path = os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
                bdd_table_id,
                bdd_table_version,
                'media',
                relative_path
            )

            if not FileHelper.is_file_exists(
                file_path=file1_path
            ):
                LoggingHelper.log_warning(
                    message=Context.get_text(
                        'warning_not_found_file',
                        file=str(file1_path)
                    )
                )
                return False

            if not FileHelper.compare_files(
                file1_path=file1_path,
                file2_path=file2_path
            ):
                LoggingHelper.log_warning(
                    message=Context.get_text(
                        'warning_differents_files',
                        file1=str(file1_path),
                        file2=str(file2_path)
                    )
                )
                return False

        return len(relative_paths) > 0

    @staticmethod
    def verify_table_pinup_media_export(
        bdd_table_id: str,
        bdd_table_version: str
    ):
        """Verify if table media export"""

        if Verifier.verify_none_value(bdd_table_id):
            return False

        if Verifier.verify_none_value(bdd_table_version):
            return False

        relative_paths = FileHelper.list_relative_paths(
            folder_path=os.path.join(
                Context.get_pinup_media_path()
            ),
            file_name=bdd_table_id,
            error_if_not_found=False
        )

        for relative_path in relative_paths:
            # Ignore cache file
            cache_file_found = False
            for cache_file_name in Constants.CACHE_FILES_NAMES:
                if cache_file_name in relative_path:
                    cache_file_found = True
                    break
            if cache_file_found:
                continue

            file1_path = os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
                bdd_table_id,
                bdd_table_version,
                'media',
                relative_path
            )

            file2_path = os.path.join(
                Context.get_pinup_media_path(),
                relative_path
            )

            if not FileHelper.is_file_exists(
                file_path=file1_path
            ):
                LoggingHelper.log_warning(
                    message=Context.get_text(
                        'warning_not_found_file',
                        file=str(file1_path)
                    )
                )
                return False

            if not FileHelper.compare_files(
                file1_path=file1_path,
                file2_path=file2_path
            ):
                LoggingHelper.log_warning(
                    message=Context.get_text(
                        'warning_differents_files',
                        file1=str(file1_path),
                        file2=str(file2_path)
                    )
                )
                return False

        return True

    @staticmethod
    def verify_table_pinup_media_uninstall(
        bdd_table_id: str,
        bdd_table_version: str
    ):
        """Verify if table media uninstall"""

        if Verifier.verify_none_value(bdd_table_id):
            return False

        if Verifier.verify_none_value(bdd_table_version):
            return False

        relative_paths = FileHelper.list_relative_paths(
            folder_path=os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
                bdd_table_id,
                bdd_table_version,
                'media'
            ),
            file_name='*',
            error_if_not_found=False
        )

        for relative_path in relative_paths:
            # Ignore cache file
            cache_file_found = False
            for cache_file_name in Constants.CACHE_FILES_NAMES:
                if cache_file_name in relative_path:
                    cache_file_found = True
                    break
            if cache_file_found:
                continue

            file_path = os.path.join(
                Context.get_pinup_media_path(),
                relative_path
            )
            if FileHelper.is_file_exists(
                file_path=file_path
            ):
                return False

        return True

    @staticmethod
    def verify_table_pinup_media_edit(
        csv_table_id: str,
        csv_table_version: str
    ):
        """Verify if table media edit"""

        relative_paths = FileHelper.list_relative_paths(
            folder_path=os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
                csv_table_id,
                csv_table_version,
                'media'
            ),
            file_name='*',
            error_if_not_found=False
        )

        parents_paths = []
        for relative_path in relative_paths:
            parent_path = os.path.basename(os.path.dirname(relative_path))
            if parent_path != 'Loading' and parent_path in parents_paths:
                return False
            parents_paths.append(parent_path)

        return True

    @staticmethod
    def verify_table_pinup_videos_install(
        csv_table_videos_path: str,
        bdd_table_id: str,
        bdd_table_version: str
    ):
        """Verify if table videos install"""

        if Verifier.verify_none_value(csv_table_videos_path):
            return None

        if Verifier.verify_none_value(bdd_table_id):
            return False

        if Verifier.verify_none_value(bdd_table_version):
            return False

        relative_paths = FileHelper.list_relative_paths(
            folder_path=os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
                bdd_table_id,
                bdd_table_version,
                'PUPVideos'
            ),
            file_name='*',
            error_if_not_found=False
        )

        for relative_path in relative_paths:
            # Ignore cache file
            cache_file_found = False
            for cache_file_name in Constants.CACHE_FILES_NAMES:
                if cache_file_name in relative_path:
                    cache_file_found = True
                    break
            if cache_file_found:
                continue

            file1_path = os.path.join(
                Context.get_pinup_path(),
                'PUPVideos',
                relative_path
            )

            file2_path = os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
                bdd_table_id,
                bdd_table_version,
                'PUPVideos',
                relative_path
            )

            if not FileHelper.is_file_exists(
                file_path=file1_path
            ):
                LoggingHelper.log_warning(
                    message=Context.get_text(
                        'warning_not_found_file',
                        file=str(file1_path)
                    )
                )
                return False

            if not FileHelper.compare_files(
                file1_path=file1_path,
                file2_path=file2_path
            ):
                LoggingHelper.log_warning(
                    message=Context.get_text(
                        'warning_differents_files',
                        file1=str(file1_path),
                        file2=str(file2_path)
                    )
                )
                return False

        return len(relative_paths) > 0

    @staticmethod
    def verify_table_pinup_videos_export(
        csv_table_videos_path: str,
        bdd_table_id: str,
        bdd_table_version: str
    ):
        """Verify if table videos export"""

        if Verifier.verify_none_value(csv_table_videos_path):
            return None

        if Verifier.verify_none_value(bdd_table_id):
            return False

        if Verifier.verify_none_value(bdd_table_version):
            return False

        relative_paths = FileHelper.list_relative_paths(
            folder_path=os.path.join(
                Context.get_pinup_path(),
                'PUPVideos',
                csv_table_videos_path
            ),
            file_name='*',
            error_if_not_found=False
        )

        for relative_path in relative_paths:
            # Ignore cache file
            cache_file_found = False
            for cache_file_name in Constants.CACHE_FILES_NAMES:
                if cache_file_name in relative_path:
                    cache_file_found = True
                    break
            if cache_file_found:
                continue

            file1_path = os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
                bdd_table_id,
                bdd_table_version,
                'PUPVideos',
                csv_table_videos_path,
                relative_path
            )

            file2_path = os.path.join(
                Context.get_pinup_path(),
                'PUPVideos',
                csv_table_videos_path,
                relative_path
            )

            if not FileHelper.is_file_exists(
                file_path=file1_path
            ):
                LoggingHelper.log_warning(
                    message=Context.get_text(
                        'warning_not_found_file',
                        file=str(file1_path)
                    )
                )
                return False

            if not FileHelper.compare_files(
                file1_path=file1_path,
                file2_path=file2_path
            ):
                LoggingHelper.log_warning(
                    message=Context.get_text(
                        'warning_differents_files',
                        file1=str(file1_path),
                        file2=str(file2_path)
                    )
                )
                return False

        return True

    @staticmethod
    def verify_table_pinup_videos_uninstall(
        csv_table_videos_path: str,
        bdd_table_id: str,
        bdd_table_version: str
    ):
        """Verify if table videos uninstall"""

        if Verifier.verify_none_value(csv_table_videos_path):
            return None

        if Verifier.verify_none_value(bdd_table_id):
            return False

        if Verifier.verify_none_value(bdd_table_version):
            return False

        relative_paths = FileHelper.list_relative_paths(
            folder_path=os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
                bdd_table_id,
                bdd_table_version,
                'PUPVideos'
            ),
            file_name='*',
            error_if_not_found=False
        )

        for relative_path in relative_paths:
            # Ignore cache file
            cache_file_found = False
            for cache_file_name in Constants.CACHE_FILES_NAMES:
                if cache_file_name in relative_path:
                    cache_file_found = True
                    break
            if cache_file_found:
                continue

            file_path = os.path.join(
                Context.get_pinup_path(),
                'PUPVideos',
                relative_path
            )
            if FileHelper.is_file_exists(
                file_path=file_path
            ):
                return False

        return True

    @staticmethod
    def verify_table_pinup_videos_edit(
        csv_table_videos_path: str,
        csv_table_id: str,
        csv_table_version: str
    ):
        """Verify if table videos uninstall"""

        if Verifier.verify_none_value(csv_table_videos_path):
            return None

        if Verifier.verify_none_value(csv_table_id):
            return False

        if Verifier.verify_none_value(csv_table_version):
            return False

        relative_paths = FileHelper.list_relative_paths(
            folder_path=os.path.join(
                Context.get_working_path(),
                'tables',
                Context.get_selected_emulator().value,
                csv_table_id,
                csv_table_version,
                'PUPVideos'
            ),
            file_name='*',
            error_if_not_found=False
        )

        return len(relative_paths) > 0

    @staticmethod
    def verify_table_xml_config_install(
        csv_table_id: str,
        csv_table_version: str,
        csv_table_rom: str
    ):
        """Verify if XML config for the rom install"""

        if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:

            if Verifier.verify_none_value(csv_table_id):
                return None

            if Verifier.verify_none_value(csv_table_version):
                return None

            if Verifier.verify_none_value(csv_table_rom):
                return None

            file_path = os.path.join(
                Context.get_working_path(),
                'tables',
                Emulator.VISUAL_PINBALL_X.value,
                csv_table_id,
                csv_table_version,
                'config',
                'B2STableSettings.xml'
            )
            if not FileHelper.is_file_exists(
                file_path=file_path
            ):
                return True

            return XmlHelper.is_tag(
                xml_file_path=os.path.join(
                    Context.get_emulator_path(
                        Context.get_selected_emulator()
                    ),
                    'Tables',
                    'B2STableSettings.xml'
                ),
                tag=csv_table_rom
            )

        return False

    @staticmethod
    def verify_table_xml_config_export(
        bdd_table_id: str,
        bdd_table_version: str,
        bdd_table_rom: str
    ):
        """Verify if XML config for the rom export"""

        if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:

            if Verifier.verify_none_value(bdd_table_id):
                return None

            if Verifier.verify_none_value(bdd_table_version):
                return None

            if Verifier.verify_none_value(bdd_table_rom):
                return None

            if not XmlHelper.is_tag(
                xml_file_path=os.path.join(
                    Context.get_emulator_path(
                    Context.get_selected_emulator()
                    ),
                    'Tables',
                    'B2STableSettings.xml'
                ),
                tag=bdd_table_rom
            ):
                return True

            file_path = os.path.join(
                Context.get_working_path(),
                'tables',
                Emulator.VISUAL_PINBALL_X.value,
                bdd_table_id,
                bdd_table_version,
                'config',
                'B2STableSettings.xml'
            )
            if not FileHelper.is_file_exists(
                file_path=file_path
            ):
                LoggingHelper.log_warning(
                    message=Context.get_text(
                        'warning_not_found_file',
                        file=str(file_path)
                    )
                )
                return False

            return True

        return False

    @staticmethod
    def verify_table_xml_config_uninstall(
        bdd_table_id: str,
        bdd_table_version: str,
        bdd_table_rom: str
    ):
        """Verify if XML config for the rom uninstall"""

        if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:

            if Verifier.verify_none_value(bdd_table_id):
                return None

            if Verifier.verify_none_value(bdd_table_version):
                return None

            if Verifier.verify_none_value(bdd_table_rom):
                return None

            file_path = os.path.join(
                Context.get_working_path(),
                'tables',
                Emulator.VISUAL_PINBALL_X.value,
                bdd_table_id,
                bdd_table_version,
                'config',
                'B2STableSettings.xml'
            )
            if not FileHelper.is_file_exists(
                file_path=file_path
            ):
                return True

            return not XmlHelper.is_tag(
                xml_file_path=os.path.join(
                    Context.get_emulator_path(
                        Context.get_selected_emulator()
                    ),
                    'Tables',
                    'B2STableSettings.xml'
                ),
                tag=bdd_table_rom
            )

        return False

    @staticmethod
    def verify_table_reg_config_install(
        csv_table_id: str,
        csv_table_version: str,
        csv_table_rom: str
    ):
        """Verify if REG config for the rom install"""

        if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:

            if Verifier.verify_none_value(csv_table_id):
                return None

            if Verifier.verify_none_value(csv_table_version):
                return None

            if Verifier.verify_none_value(csv_table_rom):
                return None

            file_path = os.path.join(
                Context.get_working_path(),
                'tables',
                Emulator.VISUAL_PINBALL_X.value,
                csv_table_id,
                csv_table_version,
                'config',
                f'user_values{Constants.REGEDIT_FILE_EXTENSION}'
            )
            if not FileHelper.is_file_exists(
                file_path=file_path
            ):
                return None

            key = Constants.VPINMAME_REG_KEY
            key += '\\'
            key += csv_table_rom
            if WinRegHelper.is_user_key_exists(
                key=key
            ):
                if WinRegHelper.is_reg_file_equal_to_registry(
                    file_path=file_path
                ):
                    return True

        return False

    @staticmethod
    def verify_table_reg_config_export(
        bdd_table_id: str,
        bdd_table_version: str,
        bdd_table_rom: str
    ):
        """Verify if REG config for the rom export"""

        if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:

            if Verifier.verify_none_value(bdd_table_id):
                return None

            if Verifier.verify_none_value(bdd_table_version):
                return None

            if Verifier.verify_none_value(bdd_table_rom):
                return None

            key = Constants.VPINMAME_REG_KEY
            key += '\\'
            key += bdd_table_rom
            if not WinRegHelper.is_user_key_exists(
                key=key
            ):
                return None

            file_path = os.path.join(
                Context.get_working_path(),
                'tables',
                Emulator.VISUAL_PINBALL_X.value,
                bdd_table_id,
                bdd_table_version,
                'config',
                f'user_values{Constants.REGEDIT_FILE_EXTENSION}'
            )
            if not FileHelper.is_file_exists(
                file_path=file_path
            ):
                LoggingHelper.log_warning(
                    message=Context.get_text(
                        'warning_not_found_file',
                        file=str(file_path)
                    )
                )
                return False

            if not WinRegHelper.is_reg_file_equal_to_registry(
                file_path=file_path
            ):
                return False

            return True

        return False

    @staticmethod
    def verify_table_reg_config_uninstall(
        bdd_table_id: str,
        bdd_table_version: str,
        bdd_table_rom: str
    ):
        """Verify if REG config for the rom uninstall"""

        if Context.get_selected_emulator() == Emulator.VISUAL_PINBALL_X:

            if Verifier.verify_none_value(bdd_table_id):
                return None

            if Verifier.verify_none_value(bdd_table_version):
                return None

            if Verifier.verify_none_value(bdd_table_rom):
                return None

            file_path = os.path.join(
                Context.get_working_path(),
                'tables',
                Emulator.VISUAL_PINBALL_X.value,
                bdd_table_id,
                bdd_table_version,
                'config',
                f'user_values{Constants.REGEDIT_FILE_EXTENSION}'
            )
            if not FileHelper.is_file_exists(
                file_path=file_path
            ):
                return None

            key = Constants.VPINMAME_REG_KEY
            key += '\\'
            key += bdd_table_rom
            return not WinRegHelper.is_user_key_exists(
                key=key
            )

        return False

    @staticmethod
    def verify_playlist_pinup_media_install(
        csv_playlist_id: str
    ):
        """Verify if playlist media exist install"""

        if Verifier.verify_none_value(csv_playlist_id):
            return False

        return len(FileHelper.list_relative_paths(
            folder_path=Context.get_pinup_media_path(),
            file_name=csv_playlist_id,
            error_if_not_found=False
        )) > 0

    @staticmethod
    def verify_playlist_pinup_media_export(
        bdd_playlist_id: str,
        bdd_playlist_version: str
    ):
        """Verify if playlist data media export"""

        if Verifier.verify_none_value(bdd_playlist_id):
            return False

        if Verifier.verify_none_value(bdd_playlist_version):
            return False

        return len(FileHelper.list_relative_paths(
            folder_path=os.path.join(
                Context.get_working_path(),
                'playlists',
                bdd_playlist_id,
                bdd_playlist_version,
                'media'
            ),
            file_name=bdd_playlist_id,
            error_if_not_found=False
        )) > 0

    @staticmethod
    def verify_playlist_pinup_media_uninstall(
        bdd_playlist_id: str
    ):
        """Verify if playlist media uninstall"""

        if Verifier.verify_none_value(bdd_playlist_id):
            return False

        return len(FileHelper.list_relative_paths(
            folder_path=Context.get_pinup_media_path(),
            file_name=bdd_playlist_id,
            error_if_not_found=False
        )) == 0

    @staticmethod
    def verify_playlist_pinup_media_edit(
        csv_playlist_id: str,
        csv_playlist_version: str
    ):
        """Verify if playlist media exist edit"""

        relative_paths = FileHelper.list_relative_paths(
            folder_path=os.path.join(
                Context.get_working_path(),
                'playlists',
                csv_playlist_id,
                csv_playlist_version,
                'media'
            ),
            file_name='*',
            error_if_not_found=False
        )

        parents_paths = []
        for relative_path in relative_paths:
            parent_path = os.path.basename(os.path.dirname(relative_path))
            if parent_path != 'Loading' and parent_path in parents_paths:
                return False
            parents_paths.append(parent_path)

        return True

    @staticmethod
    def verify_playlist_emulator_export(
        bdd_playlist_id: str,
        bdd_playlist_version: str
    ):
        """Verify if playlist export"""

        if Verifier.verify_none_value(bdd_playlist_id):
            return False

        if Verifier.verify_none_value(bdd_playlist_version):
            return False

        return len(FileHelper.list_relative_paths(
            folder_path=os.path.join(
                Context.get_working_path(),
                'playlists',
                bdd_playlist_id,
                bdd_playlist_version
            ),
            file_name='*',
            error_if_not_found=False
        )) > 0

    @staticmethod
    def verify_bdd_table(
        bdd_tables: list,
        bdd_table: str
    ):
        """Verify if BDD table exists"""

        if bdd_table not in bdd_tables:
            return False

        return BddHelper.count_rows(
            bdd_file_path=Context.get_pinup_bdd_path(),
            table_name=bdd_table
        ) > 0

    @staticmethod
    def verify_true_or_false_values(
        row: dict,
        true_or_false: bool
    ):
        """Verify if no false values in row"""

        for key, value in row.items():
            if key == Constants.UI_TABLE_KEY_COL_SELECTION:
                continue
            if not isinstance(value, bool):
                continue
            if value == true_or_false:
                return True

        return False

    @staticmethod
    def retrieve_verified_row_color(
        row: list
    ):
        """Retrieve color from a verified row"""

        # Update color
        if not Verifier.verify_true_or_false_values(
            row=row,
            true_or_false=False
        ):
            return Constants.ITEM_COLOR_GREEN

        return Constants.ITEM_COLOR_RED

    @staticmethod
    def verify_config_files_install(
        config: str
    ):
        """Verify if config files exist install"""

        config_path = os.path.join(
            Context.get_configs_path(),
            config,
            Component.FILES.name.lower()
        )

        relative_pathes = FileHelper.list_relative_paths(
            folder_path=config_path,
            file_name='*',
            error_if_not_found=False
        )

        if len(relative_pathes) == 0:
            return None

        for relative_path in relative_pathes:
            file_path = os.path.join(
                str(Context.get_pinup_path().drive) + '\\',
                relative_path
            )
            if not FileHelper.is_file_exists(
                file_path=file_path
            ):
                LoggingHelper.log_warning(
                    message=Context.get_text(
                        'warning_not_found_file',
                        file=str(file_path)
                    )
                )
                return False

        return True

    @staticmethod
    def verify_config_files_export(
        config: str
    ):
        """Verify if config files exist export"""

        config_path = os.path.join(
            Context.get_configs_path(),
            config,
            Component.FILES.name.lower()
        )

        relative_pathes = FileHelper.list_relative_paths(
            folder_path=config_path,
            file_name='*',
            error_if_not_found=False
        )

        if len(relative_pathes) == 0:
            return None

        for relative_path in relative_pathes:
            file1_path = os.path.join(
                config_path,
                relative_path
            )

            file2_path = os.path.join(
                str(Context.get_pinup_path().drive) + '\\',
                relative_path
            )

            if not FileHelper.is_file_exists(
                file_path=file1_path
            ):
                LoggingHelper.log_warning(
                    message=Context.get_text(
                        'warning_not_found_file',
                        file=str(file1_path)
                    )
                )
                return False

            if not FileHelper.compare_files(
                file1_path=file1_path,
                file2_path=file2_path
            ):
                LoggingHelper.log_warning(
                    message=Context.get_text(
                        'warning_differents_files',
                        file1=str(file1_path),
                        file2=str(file2_path)
                    )
                )
                return False

        return True

    @staticmethod
    def verify_config_files_uninstall(
        config: str
    ):
        """Verify if config files exist uninstall"""

        config_path = os.path.join(
            Context.get_configs_path(),
            config,
            Component.FILES.name.lower()
        )

        relative_pathes = FileHelper.list_relative_paths(
            folder_path=config_path,
            file_name='*',
            error_if_not_found=False
        )

        if len(relative_pathes) == 0:
            return None

        for relative_path in relative_pathes:
            file_path = os.path.join(
                str(Context.get_pinup_path().drive) + '\\',
                relative_path
            )
            if FileHelper.is_file_exists(
                file_path=file_path
            ):
                return False

        return True

    @staticmethod
    def verify_config_files_edit(
        config: str
    ):
        """Verify if config files exist edit"""

        config_path = os.path.join(
            Context.get_configs_path(),
            config,
            Component.FILES.name.lower()
        )

        relative_pathes = FileHelper.list_relative_paths(
            folder_path=config_path,
            file_name='*',
            error_if_not_found=False
        )

        if len(relative_pathes) == 0:
            return None

        return True

    @staticmethod
    def verify_config_registry_install(
        config: str
    ):
        """Verify if config registry exist install"""

        config_path = os.path.join(
            Context.get_configs_path(),
            config,
            Component.REGISTRY.name.lower()
        )

        relative_pathes = FileHelper.list_relative_paths(
            folder_path=config_path,
            file_name='*',
            error_if_not_found=False
        )

        if len(relative_pathes) == 0:
            return None

        for relative_path in relative_pathes:
            regedit_file_path = os.path.join(
                config_path,
                relative_path
            )

            for key in WinRegHelper.extract_regedit_keys(
                file_path=regedit_file_path
            ):
                if not key.startswith(Constants.REGEDIT_ROOT_KEY_NAME):
                    continue

                if not WinRegHelper.is_user_key_exists(
                    key=key[len(Constants.REGEDIT_ROOT_KEY_NAME) + 1:]
                ):
                    return False

                if not WinRegHelper.is_reg_file_equal_to_registry(
                    file_path=regedit_file_path
                ):
                    return False

        return True

    @staticmethod
    def verify_config_registry_export(
        config: str
    ):
        """Verify if config registry exist export"""

        config_path = os.path.join(
            Context.get_configs_path(),
            config,
            Component.REGISTRY.name.lower()
        )

        relative_pathes = FileHelper.list_relative_paths(
            folder_path=config_path,
            file_name='*',
            error_if_not_found=False
        )

        if len(relative_pathes) == 0:
            return None

        for relative_path in relative_pathes:
            regedit_file_path = os.path.join(
                config_path,
                relative_path
            )

            for key in WinRegHelper.extract_regedit_keys(
                file_path=regedit_file_path
            ):
                if not key.startswith(Constants.REGEDIT_ROOT_KEY_NAME):
                    continue

                if not WinRegHelper.is_user_key_exists(
                    key=key[len(Constants.REGEDIT_ROOT_KEY_NAME) + 1:]
                ):
                    continue

                if not WinRegHelper.is_reg_file_equal_to_registry(
                    file_path=regedit_file_path
                ):
                    return False

        return True

    @staticmethod
    def verify_config_registry_uninstall(
        config: str
    ):
        """Verify if config registry exist uninstall"""

        config_path = os.path.join(
            Context.get_configs_path(),
            config,
            Component.REGISTRY.name.lower()
        )

        relative_pathes = FileHelper.list_relative_paths(
            folder_path=config_path,
            file_name='*',
            error_if_not_found=False
        )

        if len(relative_pathes) == 0:
            return None

        for relative_path in relative_pathes:
            for key in WinRegHelper.extract_regedit_keys(
                file_path=os.path.join(
                    config_path,
                    relative_path
                )
            ):
                if not key.startswith(Constants.REGEDIT_ROOT_KEY_NAME):
                    continue

                if WinRegHelper.is_user_key_exists(
                    key=key[len(Constants.REGEDIT_ROOT_KEY_NAME) + 1:]
                ):
                    return False

        return True

    @staticmethod
    def verify_config_registry_edit(
        config: str
    ):
        """Verify if config registry exist edit"""

        config_path = os.path.join(
            Context.get_configs_path(),
            config,
            Component.REGISTRY.name.lower()
        )

        relative_pathes = FileHelper.list_relative_paths(
            folder_path=config_path,
            file_name='*',
            error_if_not_found=False
        )

        if len(relative_pathes) == 0:
            return None

        return True
