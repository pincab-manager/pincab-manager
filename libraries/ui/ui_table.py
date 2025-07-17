#!/usr/bin/python3
"""UI Table"""

import tkinter as tk
from tkinter import ttk

from libraries.constants.constants import Constants
from libraries.context.context import Context
from libraries.verifier.verifier import Verifier

# pylint: disable=too-many-branches, too-many-locals
# pylint: disable=too-many-statements


class UITable:
    """Class for UI Table"""

    def __init__(
        self,
        parent: any,
        on_selected_rows_change: any,
        rows: list,
        multiple_selection=True
    ):
        """Initialize table"""

        self.__on_selected_rows_changed = on_selected_rows_change
        self.__multiple_selection = multiple_selection

        # Create center frame
        center_frame = tk.Frame(parent)
        center_frame.pack(
            side=tk.TOP,
            fill=tk.BOTH,
            padx=Constants.UI_PAD_BIG,
            expand=True
        )

        # Create bottom frame
        bottom_frame = tk.Frame(parent)
        bottom_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            pady=Constants.UI_PAD_BIG
        )

        # Create buttons to select/unselect all rows
        if self.__multiple_selection:
            self.__button_select_all = tk.Button(
                bottom_frame,
                text=Context.get_text('select_all'),
                command=lambda: self.__set_selected_all_rows(True)
            )
            self.__button_select_all.pack(
                side=tk.LEFT,
                padx=Constants.UI_PAD_BIG
            )
            self.__button_deselect_all = tk.Button(
                bottom_frame,
                text=Context.get_text('deselect_all'),
                command=lambda: self.__set_selected_all_rows(False)
            )
            self.__button_deselect_all.config(state=tk.DISABLED)
            self.__button_deselect_all.pack(
                side=tk.LEFT,
                padx=Constants.UI_PAD_SMALL
            )

        # Retrieve columns ids from rows
        columns_ids = []
        if len(rows) > 0:
            for key in rows[0].keys():
                if key == Constants.UI_TABLE_KEY_COLOR:
                    continue
                if key == Constants.UI_TABLE_KEY_COL_ID:
                    continue
                columns_ids.append(key)

        # Initialize tree
        self.__tree = ttk.Treeview(
            center_frame,
            columns=tuple(columns_ids),
            show='headings',
            selectmode=tk.BROWSE
        )

        # Set columns headers
        for column_id in columns_ids:
            self.__tree.heading(
                column_id,
                text=Context.get_text(
                    column_id
                )
            )

        # Set columns size
        for column_id in columns_ids:
            width = 100
            anchor = tk.CENTER
            stretch = False
            if column_id == Constants.UI_TABLE_KEY_COL_SELECTION:
                width = 20
            elif column_id == Constants.UI_TABLE_KEY_COL_NAME:
                width = 200
                anchor = tk.W
                stretch = True
            self.__tree.column(
                column_id,
                width=width,
                anchor=anchor,
                stretch=stretch
            )

        # Create a vertical scrollbar
        scrollbar = ttk.Scrollbar(
            center_frame,
            orient=tk.VERTICAL,
            command=self.__tree.yview
        )
        self.__tree.configure(yscrollcommand=scrollbar.set)

        # Set rows
        self.set_rows(
            rows=rows
        )

        # Set position for Treeview and scrollbar
        self.__tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Call a function when row clicked
        self.__tree.bind("<ButtonRelease-1>", self.__on_row_clicked)

        # Call a function when selection changed
        self.__tree.bind("<<TreeviewSelect>>", self.__on_selection_changed)

    def __advise_selection_changed(self):
        """Advise selection rows changed"""

        if self.__multiple_selection:
            selected_rows_counter = 0
            for child_id in self.__tree.get_children():
                selected_value = self.__tree.item(child_id, "values")[0]
                if selected_value == self.__get_selected_value(
                    selected=True
                ):
                    selected_rows_counter += 1

            if selected_rows_counter == 0:
                self.__button_select_all.config(state=tk.NORMAL)
                self.__button_deselect_all.config(state=tk.DISABLED)
            elif selected_rows_counter == len(self.__tree.get_children()):
                self.__button_select_all.config(state=tk.DISABLED)
                self.__button_deselect_all.config(state=tk.NORMAL)
            else:
                self.__button_select_all.config(state=tk.NORMAL)
                self.__button_deselect_all.config(state=tk.NORMAL)

        # Advise that selected rows changed
        self.__on_selected_rows_changed()

    def __set_selected_all_rows(
        self,
        selected: bool
    ):
        """Set selected for all rows"""

        for child_id in self.__tree.get_children():
            self.__tree.item(
                child_id,
                values=(
                    self.__get_selected_value(
                        selected=selected
                    ),
                    *self.__tree.item(child_id, "values")[1:]
                )
            )

        # Advise that selection changed
        self.__advise_selection_changed()

    def __on_selection_changed(self, event):
        """Called when selection changed"""

        # Do nothing if multiple selection
        if self.__multiple_selection:
            return

        # Do nothing if selection not unique
        selected_items = event.widget.selection()
        if len(selected_items) != 1:
            return

        for child_id in self.__tree.get_children():
            selected_value = child_id in selected_items
            self.__tree.item(
                child_id,
                values=(self.__get_selected_value(selected_value), *
                        self.__tree.item(child_id, "values")[1:])
            )

        # Advise that selection changed
        self.__advise_selection_changed()

    def __on_row_clicked(self, event):
        """Called when a row is clicked"""

        # Do nothing if not multiple selection
        if not self.__multiple_selection:
            return

        # Check if click on a column header
        region = self.__tree.identify_region(event.x, event.y)
        if region == "heading":
            return

        child_id = self.__tree.identify_row(event.y)
        if child_id:
            current_value = self.__tree.item(child_id, "values")[0]
            current_selected_state = self.__is_checked_value(current_value)
            new_selected_state = self.__get_selected_value(
                not current_selected_state)

            # Toggle selected state
            self.__tree.item(
                child_id,
                values=(new_selected_state, *
                        self.__tree.item(child_id, "values")[1:])
            )

        # Advise that selection changed
        self.__advise_selection_changed()

    def __is_checked_value(
        self,
        value: str
    ):
        """Specify if checked value"""

        return value == Context.get_text('table_checked')

    def __get_checked_value(
        self,
        checked: bool
    ):
        """Get checked value"""

        if checked:
            return Context.get_text('table_checked')

        return Context.get_text('table_unchecked')

    def __get_selected_value(
        self,
        selected: bool
    ):
        """Get selected value"""

        if selected:
            return Context.get_text('table_selected')

        return Context.get_text('table_unselected')

    def list_rows(self):
        """List rows"""

        return self.__rows

    def get_selected_rows(self):
        """Get selected rows"""

        result = []
        child_idx = 0
        for child_id in self.__tree.get_children():
            child_data = self.__tree.item(child_id, "values")
            selected_value = child_data[0]
            if selected_value == self.__get_selected_value(
                selected=True
            ):
                result.append(self.__rows[child_idx])
            child_idx += 1

        return result

    def set_selected_rows(
        self,
        rows_idx: list
    ):
        """Set selected rows"""

        # Raise Exception if no multiple selection
        if not self.__multiple_selection and len(rows_idx) > 1:
            raise Exception('Cannot select multiple rows for this table!')

        # Unselect all rows
        if not self.__multiple_selection:
            self.__set_selected_all_rows(selected=False)

        # Select each row
        child_idx = 0
        for child_id in self.__tree.get_children():
            if child_idx in rows_idx:
                # Select the item and set focus on it
                self.__tree.item(
                    child_id,
                    values=(self.__get_selected_value(True), *
                            self.__tree.item(child_id, "values")[1:])
                )
                self.__tree.focus(child_id)
                self.__tree.selection_set(child_id)
            child_idx += 1

        # Set focus on tree
        self.focus()

        # Advise that selection changed
        self.__advise_selection_changed()

        # Set to position 0 if only idx 0 is selected
        if rows_idx == [0]:
            self.__tree.yview_moveto(0)

    def set_rows(
        self,
        rows: list
    ):
        """Set rows"""

        self.__rows = rows

        # Delete rows on tree
        for item in self.__tree.get_children():
            self.__tree.delete(item)

        # Add data with tag color from rows
        colors = []
        for row in rows:
            data_row = []
            color = 'black'
            for key, value in row.items():
                if key == Constants.UI_TABLE_KEY_COL_ID:
                    continue
                if key == Constants.UI_TABLE_KEY_COLOR:
                    color = value
                    if color not in colors:
                        self.__tree.tag_configure(color, foreground=color)
                        colors.append(color)
                elif key == Constants.UI_TABLE_KEY_COL_SELECTION:
                    data_row.append(self.__get_selected_value(value))
                elif isinstance(value, bool):
                    data_row.append(self.__get_checked_value(value))
                elif Verifier.verify_none_value(value):
                    data_row.append(Context.get_text('table_none_checked'))
                else:
                    data_row.append(value)
            self.__tree.insert(
                '',
                tk.END,
                values=tuple(data_row),
                tags=(color)
            )

    def focus(self):
        """Request focus"""

        self.__tree.focus_set()
