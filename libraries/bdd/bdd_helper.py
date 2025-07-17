#!/usr/bin/python3
"""BDD Helper"""

import sqlite3
from datetime import datetime

from libraries.context.context import Context
from libraries.file.file_helper import FileHelper
from libraries.constants.constants import Constants, Emulator
from libraries.logging.logging_helper import LoggingHelper


# pylint: disable=consider-using-max-builtin

class BddHelper:
    """Class to help usage of BDD"""

    @staticmethod
    def __generate_insert_sql(
        table_name: str,
        row: dict
    ):
        """Generate INSERT for SQL from a dictionary"""
        columns = ', '.join(row.keys())
        values = ', '.join(f"\'{value}\'" if value !=
                           'NULL' else value for value in row.values())

        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
        return sql

    @staticmethod
    def __get_current_datetime_formatted():
        """Get and format current datetime"""
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime(
            '%Y-%m-%d %H:%M:%S.%f')[:-3]
        return formatted_datetime

    @staticmethod
    def __execute_sql_command(
        bdd_file_path: str,
        sql_command: str
    ):
        """Execute a SQL command in the BDD"""

        if not FileHelper.is_file_exists(bdd_file_path):
            raise Exception(Context.get_text(
                'error_missing_bdd',
                bdd_file_path=bdd_file_path
            ))

        try:
            # Connect to the BDD
            conn = sqlite3.connect(bdd_file_path)
            conn.row_factory = sqlite3.Row

            # Create a cursor
            cur = conn.cursor()

            # Execute the SQL command
            cur.execute(sql_command)

            # Retrieve rows
            rows = cur.fetchall()

            # Commit any change
            conn.commit()

            # Transform each row as a dictionary
            return [dict(row) for row in rows]

        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def format_value(value: str):
        """Format value"""
        if BddHelper.is_not_null_value(
            value=value
        ):
            return value
        return 'NULL'

    @staticmethod
    def is_not_null_value(value: str):
        """Check if the value is not null"""
        if value is None:
            return False
        if str(value).upper() == 'NONE':
            return False
        if str(value).upper() == 'NULL':
            return False
        return True

    @staticmethod
    def is_not_null_dict_value(row: dict, column_id: str):
        """Check if the value in a dictionary is not null"""
        if column_id not in row:
            return False
        return BddHelper.is_not_null_value(value=row[column_id])

    @staticmethod
    def list_items(
        bdd_file_path: str,
        table_name: str
    ):
        """List items for a table"""

        return BddHelper.__execute_sql_command(
            bdd_file_path=bdd_file_path,
            sql_command=f'SELECT * FROM {table_name}'
        )

    @staticmethod
    def delete_items(
        bdd_file_path: str,
        bdd_table_name: str
    ):
        """Delete items from a BDD table"""
        if Context.is_simulated():
            LoggingHelper.log_info(
                message=Context.get_text(
                    'delete_items_simulation',
                    bdd_table_name=bdd_table_name
                )
            )
            return None

        LoggingHelper.log_info(
            message=Context.get_text(
                'delete_items_in_progress',
                bdd_table_name=bdd_table_name
            )
        )

        return BddHelper.__execute_sql_command(
            bdd_file_path=bdd_file_path,
            sql_command=f'DELETE FROM {bdd_table_name}'
        )

    @staticmethod
    def insert_items(
        bdd_file_path: str,
        bdd_table_name: str,
        items: list
    ):
        """Insert items in a BDD table"""
        if Context.is_simulated():
            LoggingHelper.log_info(
                message=Context.get_text(
                    'insert_items_simulation',
                    bdd_table_name=bdd_table_name
                )
            )
            return

        LoggingHelper.log_info(
            message=Context.get_text(
                'insert_items_in_progress',
                bdd_table_name=bdd_table_name
            )
        )

        for item in items:
            sql_command = BddHelper.__generate_insert_sql(
                table_name=bdd_table_name,
                row=item
            )

            BddHelper.__execute_sql_command(
                bdd_file_path=bdd_file_path,
                sql_command=sql_command
            )

    @staticmethod
    def list_playlists(
        bdd_file_path: str
    ):
        """List playlists"""

        if not FileHelper.is_file_exists(bdd_file_path):
            return []

        return BddHelper.__execute_sql_command(
            bdd_file_path=bdd_file_path,
            sql_command=f'SELECT * FROM PLAYLISTS ORDER BY {
                Constants.BDD_COL_PLAYLIST_NAME}'
        )

    @staticmethod
    def get_playlist(
        bdd_file_path: str,
        playlist_id: str
    ):
        """Get playlist"""

        if not FileHelper.is_file_exists(bdd_file_path):
            return None

        sql_command = 'SELECT * FROM PLAYLISTS WHERE '
        sql_command += Constants.BDD_COL_PLAYLIST_ID
        sql_command += ' = "'
        sql_command += str(playlist_id)
        sql_command += '"'
        result = BddHelper.__execute_sql_command(
            bdd_file_path=bdd_file_path,
            sql_command=sql_command
        )

        if len(result) > 0:
            return result[0]

        return None

    @staticmethod
    def insert_playlist(
        bdd_file_path: str,
        playlist_data: dict
    ):
        """Insert playlist"""

        sequence = 0
        for playlist in BddHelper.list_playlists(
            bdd_file_path=bdd_file_path
        ):
            playlist_sequence = playlist[Constants.BDD_COL_PLAYLIST_SEQUENCE]
            if sequence < playlist_sequence:
                sequence = playlist_sequence
        sequence += 1

        playlist_parent = 0
        playlist_type = 1
        if playlist_data[Constants.CSV_COL_ID] == 'pl_home':
            playlist_parent = -1
        if playlist_data[Constants.CSV_COL_ID] == 'pl_StartUP':
            playlist_type = 0

        playlist_visible = '0'
        if playlist_data[Constants.CSV_COL_AVAILABLE]:
            playlist_visible = '1'

        row = {
            Constants.BDD_COL_PLAYLIST_SEQUENCE: sequence,
            'PlayName': BddHelper.format_value(
                value=playlist_data[Constants.CSV_COL_NAME]
            ),
            'Visible': BddHelper.format_value(
                value=playlist_visible
            ),
            'DisplayOrder': '0',
            'Logo': BddHelper.format_value(
                value=playlist_data[Constants.CSV_COL_ID]
            ),
            'PlayListParent': BddHelper.format_value(
                value=playlist_parent
            ),
            Constants.BDD_COL_PLAYLIST_NAME: BddHelper.format_value(
                value=playlist_data[Constants.CSV_COL_NAME]
            ),
            Constants.BDD_COL_PLAYLIST_VERSION: BddHelper.format_value(
                value=playlist_data[Constants.CSV_COL_VERSION]
            ),
            'PlayListType': BddHelper.format_value(
                value=playlist_type
            ),
            'PlayListSQL': BddHelper.format_value(
                value=playlist_data[Constants.CSV_COL_SQL]
            ),
            'MenuColor': '16777215',
            'passcode': '0',
            'UglyList': '0',
            'HideSysLists': '0',
            'ThemeFolder': 'NULL',
            'useDefaults': '0'
        }

        sql_command = BddHelper.__generate_insert_sql(
            table_name='playlists',
            row=row
        )

        if Context.is_simulated():
            LoggingHelper.log_info(
                message=Context.get_text(
                    'insert_playlist_simulation',
                    playlist_name=playlist_data[Constants.CSV_COL_NAME]
                )
            )
            return

        LoggingHelper.log_info(
            message=Context.get_text(
                'insert_playlist_in_progress',
                playlist_name=playlist_data[Constants.CSV_COL_NAME]
            )
        )

        BddHelper.__execute_sql_command(
            bdd_file_path=bdd_file_path,
            sql_command=sql_command
        )

    @staticmethod
    def delete_playlist(
        bdd_file_path: str,
        playlist: dict
    ):
        """Delete playlist"""

        if Context.is_simulated():
            LoggingHelper.log_info(
                message=Context.get_text(
                    'delete_playlist_simulation',
                    playlist_name=playlist[Constants.BDD_COL_PLAYLIST_NAME]
                )
            )
            return

        LoggingHelper.log_info(
            message=Context.get_text(
                'delete_playlist_in_progress',
                playlist_name=playlist[Constants.BDD_COL_PLAYLIST_NAME]
            )
        )

        sql_command = 'DELETE FROM PLAYLISTS WHERE PlayListID= "'
        sql_command += str(playlist["PlayListID"])
        sql_command += '"'
        BddHelper.__execute_sql_command(
            bdd_file_path=bdd_file_path,
            sql_command=sql_command
        )

    @staticmethod
    def list_tables(
        bdd_file_path: str,
        emulator: Emulator
    ):
        """List tables"""

        if not FileHelper.is_file_exists(bdd_file_path):
            return []

        sql_command = 'SELECT * FROM GAMES WHERE EMUID='
        sql_command += str(Constants.EMULATORS_IDS[emulator])
        sql_command += f' ORDER BY {Constants.BDD_COL_TABLE_NAME}'
        return BddHelper.__execute_sql_command(
            bdd_file_path=bdd_file_path,
            sql_command=sql_command
        )

    @staticmethod
    def get_table(
        bdd_file_path: str,
        emulator: Emulator,
        table_id: str
    ):
        """Get table"""

        if not FileHelper.is_file_exists(bdd_file_path):
            return None

        sql_command = 'SELECT * FROM GAMES WHERE EMUID='
        sql_command += str(Constants.EMULATORS_IDS[emulator])
        sql_command += ' AND '
        sql_command += Constants.BDD_COL_TABLE_ID
        sql_command += ' = "'
        sql_command += str(table_id)
        sql_command += '"'
        result = BddHelper.__execute_sql_command(
            bdd_file_path=bdd_file_path,
            sql_command=sql_command
        )

        if len(result) > 0:
            return result[0]

        return None

    @staticmethod
    def insert_table(
        bdd_file_path: str,
        table_data: dict,
        emulator: Emulator
    ):
        """Insert table"""

        match emulator:
            case Emulator.VISUAL_PINBALL_X:
                table_file_extension = 'vpx'

            case Emulator.PINBALL_FX2:
                table_file_extension = 'pxp'

            case Emulator.PINBALL_FX3:
                table_file_extension = 'pxp'

            case Emulator.PINBALL_FX:
                table_file_extension = 'pxp'

            case Emulator.PINBALL_M:
                table_file_extension = 'pxp'

            case Emulator.FUTURE_PINBALL:
                table_file_extension = 'fpt'

            case _:
                raise Exception(Context.get_text(
                    'error_emulator_not_implemented',
                    emulator=emulator.value
                ))

        sequence = Constants.EMULATORS_IDS[emulator] * 1000
        for table in BddHelper.list_tables(
            bdd_file_path=bdd_file_path,
            emulator=emulator
        ):
            table_sequence = table[Constants.BDD_COL_TABLE_SEQUENCE]
            if sequence < table_sequence:
                sequence = table_sequence
        sequence += 1

        table_visible = '0'
        if table_data[Constants.CSV_COL_AVAILABLE] == Constants.CSV_YES_VALUE:
            table_visible = '1'

        file_name = table_data[Constants.CSV_COL_ID]
        file_name += '.'
        file_name += table_file_extension
        row = {
            Constants.BDD_COL_TABLE_SEQUENCE: sequence,
            'EMUID': BddHelper.format_value(
                value=Constants.EMULATORS_IDS[emulator]
            ),
            'GameName': BddHelper.format_value(
                value=table_data[Constants.CSV_COL_ID]
            ),
            Constants.BDD_COL_TABLE_GAME_FILE: BddHelper.format_value(
                value=file_name
            ),
            Constants.BDD_COL_TABLE_NAME: BddHelper.format_value(
                value=table_data[Constants.CSV_COL_NAME]
            ),
            'UseEmuDefaults': 'NULL',
            'Visible': BddHelper.format_value(
                value=table_visible
            ),
            'Notes': 'NULL',
            'DateAdded': BddHelper.__get_current_datetime_formatted(),
            'GameYear': 'NULL',
            Constants.BDD_COL_TABLE_ROM: BddHelper.format_value(
                value=table_data[Constants.CSV_COL_ROM]
            ),
            'Manufact': 'NULL',
            'NumPlayers': 'NULL',
            'ResolutionX': 'NULL',
            'ResolutionY': 'NULL',
            'OutputScreen': 'NULL',
            'ThemeColor': 'NULL',
            'GameType': 'NULL',
            'TAGS': 'NULL',
            'Category': 'NULL',
            'Author': 'NULL',
            'LaunchCustomVar': 'NULL',
            'GKeepDisplays': 'NULL',
            'GameTheme': 'NULL',
            'GameRating': 'NULL',
            'Special': 'NULL',
            'sysVolume': 'NULL',
            'DOFStuff': 'NULL',
            'MediaSearch': 'NULL',
            'AudioChannels': 'NULL',
            'CUSTOM3': 'NULL',
            Constants.BDD_COL_TABLE_VERSION: BddHelper.format_value(
                value=table_data[Constants.CSV_COL_VERSION]
            ),
            'ALTEXE': BddHelper.format_value(
                value=table_data[Constants.CSV_COL_ALT_EXE]
            ),
            'IPDBNum': 'NULL',
            'DateUpdated': 'NULL',
            'DateFileUpdated': 'NULL',
            'AutoRecFlag': '0',
            'AltRunMode': BddHelper.format_value(
                value=table_data[Constants.CSV_COL_ALT_RUN_MODE]
            ),
            'WebLinkURL': BddHelper.format_value(
                value=table_data[Constants.CSV_COL_WEBLINK_URL]
            ),
            'DesignedBy': 'NULL',
            'CUSTOM4': 'NULL',
            'CUSTOM5': 'NULL',
            'WEBGameID': 'NULL',
            'ROMALT': 'NULL',
            'ISMOD': '0',
            'FLAG1': '0',
            'FLAG2': '0',
            'FLAG3': '0',
            'gLog': 'NULL',
            'RatingWeb': 'NULL',
            'WebLink2URL': BddHelper.format_value(
                value=table_data[Constants.CSV_COL_WEBLINK2_URL]
            ),
            'TourneyID': 'NULL',
            Constants.BDD_COL_VIDEOS_PATH: BddHelper.format_value(
                value=table_data[Constants.CSV_COL_VIDEOS_PATH]
            )
        }

        sql_command = BddHelper.__generate_insert_sql(
            table_name='games',
            row=row
        )

        if Context.is_simulated():
            LoggingHelper.log_info(
                message=Context.get_text(
                    'insert_table_simulation',
                    table_name=table_data[Constants.CSV_COL_ID]
                )
            )
            return

        LoggingHelper.log_info(
            message=Context.get_text(
                'insert_table_in_progress',
                table_name=table_data[Constants.CSV_COL_ID]
            )
        )

        BddHelper.__execute_sql_command(
            bdd_file_path=bdd_file_path,
            sql_command=sql_command
        )

    @staticmethod
    def delete_table(
        bdd_file_path: str,
        table: dict
    ):
        """Delete table"""

        if Context.is_simulated():
            LoggingHelper.log_info(
                message=Context.get_text(
                    'delete_table_simulation',
                    table_name=table["GameName"]
                )
            )
            return

        LoggingHelper.log_info(
            message=Context.get_text(
                'delete_table_in_progress',
                table_name=table["GameName"]
            )
        )

        BddHelper.__execute_sql_command(
            bdd_file_path=bdd_file_path,
            sql_command=f'DELETE FROM GAMES WHERE GameID = "{table["GameID"]}"'
        )

    @staticmethod
    def list_bdd_tables(
        bdd_file_path: str
    ):
        """List BDD Tables"""

        result = []
        for table in BddHelper.__execute_sql_command(
            bdd_file_path=bdd_file_path,
            sql_command="SELECT name FROM sqlite_master WHERE type = 'table';"
        ):
            result.append(table['name'])

        return result

    @staticmethod
    def count_rows(
        bdd_file_path: str,
        table_name: str
    ):
        """Count rows for the specified table"""

        sql_command = 'SELECT * FROM '
        sql_command += table_name
        result = BddHelper.__execute_sql_command(
            bdd_file_path=bdd_file_path,
            sql_command=sql_command
        )

        return len(result)
