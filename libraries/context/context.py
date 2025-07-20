#!/usr/bin/python3
"""Context"""

import json
import sys
import os
from pathlib import Path
import re
import socket
import configparser
import locale

from selenium import webdriver

from libraries.constants.constants import Action, Category, Component, Emulator, Constants, Media

# pylint: disable=unnecessary-comprehension
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-branches
# pylint: disable=protected-access


class Context:
    """Class to store context"""

    __initialized: bool = False
    __hostname: str = None
    __app_version: str = None
    __lang_code: str = None
    __monitor: int = None
    __texts = {}
    __pinup_path: Path = None
    __steam_path: Path = None
    __emulators_paths: dict[Emulator, Path] = {}
    __selected_category: Category = None
    __selected_emulator: Emulator = None
    __selected_action: Action = None
    __selected_components = []
    __selected_tables_rows = []
    __selected_playlists_rows = []
    __selected_bdd_tables_rows = []
    __selected_configs_rows = []
    __selected_folder_path = None
    __simulated: bool = False
    __auto_refresh: bool = True
    __available_emulators = []
    __available_media = []
    __screen_number_by_media = {}
    __selenium_web_browser = None
    __working_path = None
    __base_path = None
    __packaged = False

    @staticmethod
    def init():
        """Initialize context"""

        if Context.__initialized:
            raise Exception(Context.get_text(
                'error_context_initialized'
            ))

        # Retrieve hostname
        Context.__hostname = socket.gethostname().lower()

        # Define working path
        pincab_manager_path = os.getenv("PINCAB_MANAGER_PATH")
        if pincab_manager_path is not None:
            Context.__working_path = pincab_manager_path
        else:
            Context.__working_path = os.getcwd()

        # Define base path depending on DEV or package
        try:
            Context.__base_path = sys._MEIPASS
            Context.__packaged = True
        except AttributeError:
            Context.__base_path = os.getcwd()
            Context.__packaged = False

        # Retrieve application's version
        try:
            with open(Context.__base_path + '/CHANGELOG', 'r', encoding='utf-8') as file:
                first_line = file.readline().strip()
                match = re.search(r'R(\d+\.\d+\.\d+)', first_line)
                if not match:
                    raise Exception('Cannot find app_version in CHANGELOG')
                Context.__app_version = match.group(1)
        except Exception:
            Context.__app_version = 'UNKNOWN'

        # Retrieve lang's code from OS language
        lang = locale.getlocale()[0]
        Context.__lang_code = 'fr' if lang.startswith('fr') else 'en'

        # Initialize paths
        Context.__pinup_path = ''
        Context.__steam_path = ''
        for emulator in Emulator:
            Context.__emulators_paths[emulator] = ''

        # Initialize monitor
        Context.__monitor = 0

        # Initialize boolean simulated
        Context.__simulated = False

        # Initialize boolean auto refresh
        Context.__auto_refresh = True

        # Specify that context is initialized
        Context.__initialized = True

        # Update context from setup
        Context.update_context_from_setup()

    @staticmethod
    def destroy():
        """Destroy context"""

        if Context.__initialized:
            Context.destroy_selenium_web_browser()
            Context.__initialized = False

    @staticmethod
    def init_selenium_web_browser():
        """Initialize Selenium Web Browser"""

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--window-position=-32000,-32000")
        chrome_options.add_argument("--window-size=1,1")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-logging"]
        )
        Context.__selenium_web_browser = webdriver.Chrome(
            options=chrome_options
        )
        Context.__selenium_web_browser.minimize_window()

    @staticmethod
    def destroy_selenium_web_browser():
        """Destroy Selenium Web Browser"""

        if Context.__selenium_web_browser is not None:
            Context.__selenium_web_browser.quit()
            Context.__selenium_web_browser = None

    @staticmethod
    def get_hostname() -> str:
        """Get hostname"""

        if not Context.__initialized:
            Context.init()

        return Context.__hostname

    @staticmethod
    def get_working_path() -> str:
        """Get working path"""

        if not Context.__initialized:
            Context.init()

        return Context.__working_path

    @staticmethod
    def get_base_path() -> str:
        """Get base path"""

        if not Context.__initialized:
            Context.init()

        return Context.__base_path

    @staticmethod
    def get_app_version() -> str:
        """Get application's version"""

        if not Context.__initialized:
            Context.init()

        return Context.__app_version

    @staticmethod
    def get_lang_code() -> str:
        """Get lang code"""

        if not Context.__initialized:
            Context.init()

        return Context.__lang_code

    @staticmethod
    def get_text(text_id: str, **kwargs) -> str:
        """Get text from its id"""

        if not Context.__initialized:
            Context.init()

        return Context.__texts[text_id].format(**kwargs)

    @staticmethod
    def get_selected_category() -> Category:
        """Get selected category"""

        if not Context.__initialized:
            Context.init()

        return Context.__selected_category

    @staticmethod
    def set_selected_category(category: Category):
        """Set selected category"""

        if not Context.__initialized:
            Context.init()

        Context.__selected_category = category

    @staticmethod
    def get_selected_emulator() -> Emulator:
        """Get selected emulator"""

        if not Context.__initialized:
            Context.init()

        return Context.__selected_emulator

    @staticmethod
    def set_selected_emulator(emulator: Emulator):
        """Set selected emulator"""

        if not Context.__initialized:
            Context.init()

        Context.__selected_emulator = emulator

    @staticmethod
    def get_selected_action() -> Action:
        """Get selected action"""

        if not Context.__initialized:
            Context.init()

        return Context.__selected_action

    @staticmethod
    def set_selected_action(action: Action):
        """Set selected action"""

        if not Context.__initialized:
            Context.init()

        Context.__selected_action = action

    @staticmethod
    def get_selected_components() -> list[Component]:
        """Get selected components"""

        if not Context.__initialized:
            Context.init()

        return Context.__selected_components

    @staticmethod
    def set_selected_components(components_items: list):
        """Set selected components"""

        if not Context.__initialized:
            Context.init()

        components_labels = []
        for components_item in components_items:
            components_labels.append(
                components_item[Constants.UI_TABLE_KEY_COL_NAME]
            )

        result = []
        for component in Component:
            if Context.get_text(component.value) in components_labels:
                result.append(component)

        Context.__selected_components = result

    @staticmethod
    def get_selected_tables_rows() -> list:
        """Get selected tables rows"""

        if not Context.__initialized:
            Context.init()

        return Context.__selected_tables_rows

    @staticmethod
    def set_selected_tables_rows(tables_rows: list):
        """Set selected tables rows"""

        if not Context.__initialized:
            Context.init()

        Context.__selected_tables_rows = tables_rows

    @staticmethod
    def get_selected_playlists_rows() -> list:
        """Get selected playlists rows"""

        if not Context.__initialized:
            Context.init()

        return Context.__selected_playlists_rows

    @staticmethod
    def set_selected_playlists_rows(playlists_rows: list):
        """Set selected playlists rows"""

        if not Context.__initialized:
            Context.init()

        Context.__selected_playlists_rows = playlists_rows

    @staticmethod
    def get_selected_bdd_tables_rows() -> list:
        """Get selected BDD Tables rows"""

        if not Context.__initialized:
            Context.init()

        return Context.__selected_bdd_tables_rows

    @staticmethod
    def set_selected_bdd_tables_rows(bdd_tables_rows: list):
        """Set selected BDD Tables rows"""

        if not Context.__initialized:
            Context.init()

        Context.__selected_bdd_tables_rows = bdd_tables_rows

    @staticmethod
    def get_selected_configs_rows() -> list:
        """Get selected configs rows"""

        if not Context.__initialized:
            Context.init()

        return Context.__selected_configs_rows

    @staticmethod
    def set_selected_configs_rows(configs_rows: list):
        """Set selected configs rows"""

        if not Context.__initialized:
            Context.init()

        Context.__selected_configs_rows = configs_rows

    @staticmethod
    def get_selected_folder_path() -> str:
        """Get selected folder's path"""

        if not Context.__initialized:
            Context.init()

        return Context.__selected_folder_path

    @staticmethod
    def set_selected_folder_path(folder_path: str):
        """Set selected folder's path"""

        if not Context.__initialized:
            Context.init()

        Context.__selected_folder_path = folder_path

    @staticmethod
    def get_selected_rows_csv_path():
        """Get CSV path describing rows for selection"""

        file_name = 'rows_'
        file_name += Context.get_selected_category().value.split('_')[
            1].lower()
        if Context.get_selected_category() == Category.TABLES:
            file_name += '_'
            file_name += Context.get_selected_emulator().value.lower()
        file_name += '_'
        file_name += Context.get_selected_action().value.split('_')[1].lower()
        return Path(os.path.join(
            Context.get_cache_path(),
            f'{file_name}.csv'
        ))

    @staticmethod
    def get_pinup_path() -> Path:
        """Get PINUP path"""

        if not Context.__initialized:
            Context.init()

        return Context.__pinup_path

    @staticmethod
    def get_steam_path() -> Path:
        """Get STEAM path"""

        if not Context.__initialized:
            Context.init()

        return Context.__steam_path

    @staticmethod
    def get_emulator_path(
        emulator: Emulator
    ) -> Path:
        """Get emulator path"""

        if not Context.__initialized:
            Context.init()

        return Context.__emulators_paths[emulator]

    @staticmethod
    def get_configs_path() -> Path:
        """Get configs path"""

        if not Context.__initialized:
            Context.init()

        return os.path.join(
            Context.get_working_path(),
            'configs'
        )

    @staticmethod
    def get_monitor() -> int:
        """Get monitor"""

        if not Context.__initialized:
            Context.init()

        return Context.__monitor

    @staticmethod
    def get_setup_file_path() -> Path:
        """Get setup file path"""

        if not Context.__initialized:
            Context.init()

        return Path(os.path.join(
            Context.get_working_path(),
            'setup',
            f'{Context.get_hostname()}.cfg'
        ))

    @staticmethod
    def get_logs_path() -> Path:
        """Get logs path"""

        if not Context.__initialized:
            Context.init()

        return Path(os.path.join(
            Context.get_working_path(),
            'logs'
        ))

    @staticmethod
    def get_cache_path():
        """Get cache path"""

        if not Context.__initialized:
            Context.init()

        return Path(os.path.join(
            Context.get_working_path(),
            'cache'
        ))

    @staticmethod
    def get_bdd_path():
        """Get database path"""

        if not Context.__initialized:
            Context.init()

        return Path(os.path.join(
            Context.get_working_path(),
            'database'
        ))

    @staticmethod
    def get_binaries_path() -> Path:
        """Get binaries path"""

        if not Context.__initialized:
            Context.init()

        return Path(os.path.join(
            Context.get_base_path(),
            'binaries'
        ))

    @staticmethod
    def get_ffmpeg_path() -> Path:
        """Get ffmpeg path"""

        if not Context.__initialized:
            Context.init()

        return Path(os.path.join(
            Context.get_binaries_path(),
            'ffmpeg.exe'
        ))

    @staticmethod
    def get_yt_dlp_path() -> Path:
        """Get yt dlp path"""

        if not Context.__initialized:
            Context.init()

        return Path(os.path.join(
            Context.get_binaries_path(),
            'yt-dlp.exe'
        ))

    @staticmethod
    def get_csv_path() -> Path:
        """Get CSV path"""

        if not Context.__initialized:
            Context.init()

        match(Context.get_selected_category()):
            case Category.TABLES:
                return Path(os.path.join(
                    Context.get_bdd_path(),
                    Context.get_selected_emulator().value,
                    'tables.csv'
                ))

            case Category.PLAYLISTS:
                return Path(os.path.join(
                    Context.get_bdd_path(),
                    Constants.COMMON_PATH,
                    'playlists.csv'
                ))

        return None

    @staticmethod
    def get_pinup_bdd_path() -> Path:
        """Get PinUp BDD path"""

        if not Context.__initialized:
            Context.init()

        return Path(os.path.join(
            Context.get_pinup_path(),
            'PUPDatabase.db'
        ))

    @staticmethod
    def get_pinup_media_path() -> Path:
        """Get PinUp media path"""

        if not Context.__initialized:
            Context.init()

        match(Context.get_selected_category()):
            case Category.TABLES:
                return Path(os.path.join(
                    Context.get_pinup_path(),
                    'POPMedia',
                    Context.get_selected_emulator().value
                ))

            case Category.PLAYLISTS:
                return Path(os.path.join(
                    Context.get_pinup_path(),
                    'POPMedia',
                    'Default'
                ))

        return None

    @staticmethod
    def is_packaged() -> bool:
        """Specify if app is packaged"""

        if not Context.__initialized:
            Context.init()

        return Context.__packaged

    @staticmethod
    def is_simulated() -> bool:
        """Specify if app is simulated"""

        if not Context.__initialized:
            Context.init()

        return Context.__simulated

    @staticmethod
    def is_auto_refresh() -> bool:
        """Specify if app is auto refresh"""

        if not Context.__initialized:
            Context.init()

        return Context.__auto_refresh

    @staticmethod
    def list_available_emulators() -> list:
        """List available emulators"""

        if not Context.__initialized:
            Context.init()

        return Context.__available_emulators

    @staticmethod
    def list_available_media() -> list:
        """List available media"""

        if not Context.__initialized:
            Context.init()

        return Context.__available_media

    @staticmethod
    def get_screen_number_by_media() -> dict:
        """Get screen number by media"""

        if not Context.__initialized:
            Context.init()

        return Context.__screen_number_by_media

    @staticmethod
    def update_context_from_setup():
        """Update context from setup"""

        if not Context.__initialized:
            Context.init()

        # If setup file exists, retrieve context from it
        if Context.get_setup_file_path().exists():
            setup = configparser.ConfigParser()
            with open(Context.get_setup_file_path(), encoding='utf-8') as file:
                setup.read_file(file)

            setup_items = {
                key: value for key, value in setup.items('DEFAULT')
            }
            if Constants.SETUP_LANG_CODE in setup_items:
                Context.__lang_code = setup_items[
                    Constants.SETUP_LANG_CODE
                ]

            if Constants.SETUP_MONITOR in setup_items:
                Context.__monitor = int(setup_items[
                    Constants.SETUP_MONITOR
                ])

            if Constants.SETUP_PINUP_PATH in setup_items:
                Context.__pinup_path = Path(setup_items[
                    Constants.SETUP_PINUP_PATH
                ])

            if Constants.SETUP_VPX_PATH in setup_items:
                Context.__emulators_paths[
                    Emulator.VISUAL_PINBALL_X
                ] = Path(setup_items[
                    Constants.SETUP_VPX_PATH
                ])

            if Constants.SETUP_FP_PATH in setup_items:
                Context.__emulators_paths[
                    Emulator.FUTURE_PINBALL
                ] = Path(setup_items[
                    Constants.SETUP_FP_PATH
                ])

            if Constants.SETUP_STEAM_PATH in setup_items:
                Context.__steam_path = Path(setup_items[
                    Constants.SETUP_STEAM_PATH
                ])
                Context.__emulators_paths[
                    Emulator.PINBALL_FX
                ] = os.path.join(
                    Context.__steam_path,
                    'steamapps',
                    Constants.COMMON_PATH,
                    'Pinball FX'
                )
                Context.__emulators_paths[
                    Emulator.PINBALL_FX2
                ] = os.path.join(
                    Context.__steam_path,
                    'steamapps',
                    Constants.COMMON_PATH,
                    'Pinball FX2'
                )
                Context.__emulators_paths[
                    Emulator.PINBALL_M
                ] = os.path.join(
                    Context.__steam_path,
                    'steamapps',
                    Constants.COMMON_PATH,
                    'Pinball M'
                )

            if Constants.SETUP_SIMULATED in setup_items:
                Context.__simulated = setup_items[
                    Constants.SETUP_SIMULATED
                ] == 'True'

            if Constants.SETUP_AUTO_REFRESH in setup_items:
                Context.__auto_refresh = setup_items[
                    Constants.SETUP_AUTO_REFRESH
                ] == 'True'

            if Constants.SETUP_AVAILABLE_EMULATORS in setup_items:
                Context.__available_emulators = []
                for emulator in Emulator:
                    if f"'{emulator.value}'" in setup_items[
                        Constants.SETUP_AVAILABLE_EMULATORS
                    ]:
                        Context.__available_emulators.append(emulator.value)

            if Constants.SETUP_AVAILABLE_MEDIA in setup_items:
                Context.__available_media = []
                for media in Media:
                    if media.value in setup_items[
                        Constants.SETUP_AVAILABLE_MEDIA
                    ]:
                        Context.__available_media.append(media.value)

            if Constants.SETUP_SCREEN_NUMBER_BY_MEDIA in setup_items:
                Context.__screen_number_by_media = json.loads(
                    setup_items[
                        Constants.SETUP_SCREEN_NUMBER_BY_MEDIA
                    ].replace('\'', '\"')
                )

        # Retrieve texts properties from lang's code
        texts_properties = configparser.ConfigParser()
        lang_path = os.path.join(
            Context.get_base_path(),
            Constants.RESOURCES_PATH,
            'lang',
            f'messages_{Context.__lang_code}.properties'
        )
        with open(lang_path, encoding='utf-8') as file:
            texts_properties.read_file(file)
        Context.__texts = {
            key: value for key, value in texts_properties.items('DEFAULT')
        }

    @staticmethod
    def get_selenium_web_browser() -> dict:
        """Get selenium web browser"""

        if not Context.__initialized:
            Context.init()

        if Context.__selenium_web_browser is None:
            Context.init_selenium_web_browser()

        return Context.__selenium_web_browser
