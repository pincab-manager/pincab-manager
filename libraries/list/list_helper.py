#!/usr/bin/python3
"""List Helper"""


class ListHelper:
    """Class to help usage of List"""

    @staticmethod
    def format_value(value: str):
        """Format value"""
        if value is None or value == 'NULL' or len(value) == 0:
            return None
        return value.strip().replace('\r\n', '').replace('\"', '').replace('\'', '')

    @staticmethod
    def retrieve_duplicated_ids(
        list1: list,
        list2: list,
        id_column1: str,
        id_column2: str
    ):
        """Retrieve duplicated ids"""
        # Use a set to store duplicated ID values
        result = set()

        # Retrieve duplicated ids from the 2 lists
        for item1 in list1:
            id_value1 = item1[id_column1]
            for item2 in list2:
                id_value2 = item2[id_column2]
                if ListHelper.format_value(id_value1) == ListHelper.format_value(id_value2):
                    result.add(ListHelper.format_value(id_value1))
                    break

        return result

    @staticmethod
    def select_items(
        ids: set,
        a_list: list,
        id_column: str
    ):
        """Select items from a list of ids"""

        result = []
        for item in a_list:
            if item[id_column] in ids:
                result.append(item)

        return result

    @staticmethod
    def select_item(
        item_id: str,
        a_list: list,
        id_column: str
    ):
        """Select item from an id"""

        for item in a_list:
            if item[id_column] == item_id:
                return item

        return {}

    @staticmethod
    def remove_items(
        ids: set,
        a_list: list,
        id_column: str
    ):
        """Remove items from a list of ids"""

        # New list
        result = []

        # Iterate through the list
        for item in a_list:
            id_value = item[id_column]
            if ListHelper.format_value(id_value) not in ids:
                result.append(item)

        return result

    @staticmethod
    def replace_item(
        a_list: list,
        item: dict,
        id_column: str
    ):
        """Replace an item identified by its id"""

        result = ListHelper.remove_items(
            ids=[item[id_column]],
            a_list=a_list,
            id_column=id_column
        )

        result.append(item)

        return result
