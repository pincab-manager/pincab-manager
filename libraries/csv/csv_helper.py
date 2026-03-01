#!/usr/bin/python3
"""CSV Helper"""

import csv
import os

from libraries.constants.constants import Constants
from libraries.context.context import Context
from libraries.file.file_helper import FileHelper
from libraries.list.list_helper import ListHelper
from libraries.logging.logging_helper import LoggingHelper


# pylint: disable=unnecessary-comprehension

class CsvHelper:
    """Class to help usage of CSV"""

    @staticmethod
    def write_data(
        file_path: str,
        data: list,
        sort_column_id=Constants.CSV_COL_NAME
    ):
        """Write data in a CSV file"""

        if Context.is_simulated():
            LoggingHelper.log_info(
                message=Context.get_text(
                    'write_data_simulation',
                    file=file_path
                )
            )
            return

        LoggingHelper.log_info(
            message=Context.get_text(
                'write_data_in_progress',
                file=file_path
            )
        )

        if not FileHelper.is_file_exists(
            file_path=file_path
        ):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(
            file_path,
            mode='w',
            newline='',
            encoding='UTF-8'
        ) as csv_file:
            # Retrieve header
            header = []
            for item in data:
                for key in item.keys():
                    if key not in header:
                        header.append(key)

            # Write header
            writer = csv.DictWriter(csv_file, fieldnames=header)
            writer.writeheader()

            # Sort data
            if len(sort_column_id) > 0:
                sorted_data = sorted(
                    data, key=lambda item: item[sort_column_id])
            else:
                sorted_data = data

            # Build rows from sorted data
            rows = []
            for data_row in sorted_data:
                row = {}
                for key in header:
                    if key not in data_row:
                        data_row[key] = None
                    row[key] = str(ListHelper.format_value(
                        value=str(data_row[key])
                    ))
                rows.append(row)
            writer.writerows(rows)

    @staticmethod
    def read_data(
        file_path: str
    ):
        """Read data from a CSV file"""

        if not FileHelper.is_file_exists(
            file_path=file_path
        ):
            return []

        with open(
            file_path,
            mode='r',
            encoding='UTF-8'
        ) as csv_file:
            reader = csv.DictReader(csv_file)
            data = [row for row in reader]
            return data
