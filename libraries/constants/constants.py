#!/usr/bin/python3
"""Constants"""

from enum import Enum


class Category(Enum):
    """Category"""

    TABLES = 'category_tables'
    PLAYLISTS = 'category_playlists'
    BDD_TABLES = 'category_bdd_tables'
    CONFIGS = 'category_configs'


class Component(Enum):
    """Component"""

    CONFIG_XML = 'component_config_xml'
    CONFIG_REG = 'component_config_reg'
    EMULATOR_PLAYLIST = 'component_emulator_playlist'
    EMULATOR_TABLE = 'component_emulator_table'
    PINUP_MEDIA = 'component_pinup_media'
    PINUP_VIDEOS = 'component_pinup_videos'
    PINUP_DATABASE = 'component_pinup_database'
    FILES = 'component_files'
    REGISTRY = 'component_registry'


class Action(Enum):
    """Action"""

    INSTALL = 'action_install'
    UNINSTALL = 'action_uninstall'
    EXPORT = 'action_export'
    COPY = 'action_copy'
    EDIT = 'action_edit'


class Media(Enum):
    """Media"""

    TOPPER = 'media_topper'
    BACKGLASS = 'media_backglass'
    FULL_DMD = 'media_full_dmd'
    PLAYFIELD = 'media_playfield'
    AUDIO = 'media_audio'
    DMD = 'media_dmd'
    FLYER = 'media_flyer'
    HELP = 'media_help'
    OTHER = 'media_other'
    WHEEL_BAR = 'media_wheel_bar'
    WHEEL_IMAGE = 'media_wheel_image'


class Emulator(Enum):
    """Emulator"""

    VISUAL_PINBALL_X = 'Visual Pinball X'
    PINBALL_FX2 = 'Pinball FX2'
    PINBALL_FX3 = 'Pinball FX3'
    PINBALL_FX = 'Pinball FX'
    PINBALL_M = 'Pinball M'
    FUTURE_PINBALL = 'Future Pinball'


class Constants:
    """Class to store constants"""

    # Constants for regedit key
    VPINMAME_REG_KEY = 'Software\\Freeware\\Visual PinMame'

    # Constants for emulators
    EMULATORS_IDS = {
        Emulator.VISUAL_PINBALL_X: 1,
        Emulator.PINBALL_FX2: 2,
        Emulator.PINBALL_FX3: 3,
        Emulator.PINBALL_FX: 6,
        Emulator.PINBALL_M: 7,
        Emulator.FUTURE_PINBALL: 4
    }

    # Constants for paths
    RESOURCES_PATH = 'resources'
    CONFIGS_PATH = 'configs'
    COMMON_PATH = 'common'

    # Constants for cache
    CACHE_FILES_NAMES = [
        'thumb',
        'pthumbs',
        'Thumbs'
    ]

    # Constants for UI
    UI_PAD_SMALL = 5
    UI_PAD_BIG = 10
    UI_TABLE_KEY_COL_SELECTION = 'column_title_selection'
    UI_TABLE_KEY_COL_ID = 'column_title_id'
    UI_TABLE_KEY_COL_NAME = 'column_title_name'
    UI_TABLE_KEY_COL_LATEST_VERSION = 'column_title_latest_version'
    UI_TABLE_KEY_COL_UNIQUE_VERSION = 'column_title_unique_version'
    UI_TABLE_KEY_COLOR = 'color'

    # Constants for setup
    SETUP_LANG_CODE = 'lang_code'
    SETUP_PINUP_PATH = 'pinup_path'
    SETUP_VPX_PATH = 'vpx_path'
    SETUP_FP_PATH = 'fp_path'
    SETUP_STEAM_PATH = 'steam_path'
    SETUP_MONITOR = 'monitor'
    SETUP_SIMULATED = 'simulated'
    SETUP_AVAILABLE_EMULATORS = 'available_emulators'
    SETUP_AVAILABLE_MEDIA = 'available_media'
    SETUP_SCREEN_NUMBER_BY_MEDIA = 'screen_number_by_media'

    # Constants for item color
    ITEM_COLOR_BLACK = 'black'
    ITEM_COLOR_GREEN = 'green'
    ITEM_COLOR_ORANGE = 'orange'
    ITEM_COLOR_RED = 'red'

    # Constants for paths
    LATEST_PATH = 'latest'

    # Constants for PinUP Bdd Tables
    PINUP_BDD_TABLES = [
        'PinUPFunctions',
        'Screens',
        'Emulators',
        'GlobalSettings',
        'GamesStats'
    ]

    # Constants for configs
    CONFIG_TEXT_PREFIX = 'config_'
    CONFIGS = [
        'dof',
        'doflinx',
        'future_pinball',
        'pinup',
        'scripts',
        'visual_pinball',
        'vpinspa',
        'x360ce'
    ]

    # Constants for BDD
    BDD_COL_TABLE_ID = 'GameName'
    BDD_COL_TABLE_NAME = 'GameDisplay'
    BDD_COL_TABLE_SEQUENCE = 'GameID'
    BDD_COL_PLAYLIST_ID = 'Logo'
    BDD_COL_PLAYLIST_SEQUENCE = 'PlayListID'
    BDD_COL_PLAYLIST_NAME = 'PlayDisplay'
    BDD_COL_PLAYLIST_VERSION = 'Notes'
    BDD_COL_VIDEOS_PATH = 'CUSTOM2'
    BDD_COL_TABLE_ROM = 'ROM'
    BDD_COL_TABLE_VERSION = 'GAMEVER'
    BDD_COL_TABLE_GAME_FILE = 'GameFileName'

    # Constants for CSV
    CSV_YES_VALUE = 'YES'
    CSV_NO_VALUE = 'NO'
    CSV_COL_NAME = 'NAME'
    CSV_COL_AVAILABLE = 'AVAILABLE'
    CSV_COL_VERSION = 'VERSION'
    CSV_COL_ID = 'ID'
    CSV_COL_SQL = 'SQL'
    CSV_COL_ALT_EXE = 'ALT_EXE'
    CSV_COL_ALT_RUN_MODE = 'ALT_RUN_MODE'
    CSV_COL_ROM = 'ROM'
    CSV_COL_VIDEOS_PATH = 'VIDEOS_PATH'
    CSV_COL_WEBLINK_URL = 'WEBLINK_URL'
    CSV_COL_WEBLINK2_URL = 'WEBLINK2_URL'

    # Constants for VLC
    VLC_SUPPORTED_EXTENSIONS = {
        # Video
        '.mp4', '.m4v', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
        '.mpg', '.mpeg', '.mpe', '.3gp', '.3g2', '.ogv', '.asf', '.ts',
        '.m2ts', '.dv', '.rmvb', '.vob', '.hevc', '.h265',
        # Audio
        '.mp3', '.flac', '.wav', '.aac', '.ogg', '.wma', '.m4a', '.caf',
        '.opus', '.midi', '.mid', '.ape', '.dsf', '.dff',
        # Image
        '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'
    }

    # Constants for PINUP VIDEOS BATCH
    PINUP_VIDEOS_BATCH_EXTENSIONS = {
        '.bat'
    }

    # Regedit constants
    REGEDIT_ROOT_KEY_NAME = 'HKEY_CURRENT_USER'
    REGEDIT_KEY_SEPARATOR = '\\'
    REGEDIT_FILE_EXTENSION = '.reg'
    REGEDIT_FILE_ENCODING = 'UTF-8'
