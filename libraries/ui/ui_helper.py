#!/usr/bin/python3
"""UI Helper"""

from tkinter import Widget, Wm, ttk

import screeninfo

from libraries.context.context import Context
from libraries.logging.logging_helper import LoggingHelper


class UIHelper:
    """Class to help usage of UI"""

    @staticmethod
    def update_combo_width(
        combo: ttk.Combobox
    ):
        """Update combo's width depending on its items"""

        max_length = max(len(item) for item in combo.cget("values"))
        combo.config(width=max_length)

    @staticmethod
    def clear_frame(
        frame: Widget
    ):
        """Clear a frame"""

        for widget in frame.winfo_children():
            widget.destroy()

    @staticmethod
    def center_window(
        window: Wm,
        width: int,
        height: int
    ):
        """Center window depending on its width and its height"""

        monitor = screeninfo.get_monitors()[Context.get_monitor()]
        screen_width = monitor.width
        screen_height = monitor.height
        x = monitor.x + (screen_width - width) // 2
        y = monitor.y + (screen_height - height) // 2
        window.geometry(f'{width}x{height}+{x}+{y}')

    @staticmethod
    def center_dialog(
        dialog: Wm,
        width: int,
        height: int,
        resizable=False,
        tool_window=True
    ):
        """Center dialog depending on its width and its height"""

        # Set dialog as tool's window
        if tool_window:
            try:
                dialog.attributes("-toolwindow", True)
            except Exception as exc:
                LoggingHelper.log_error(
                    message=Context.get_text(
                        'error_unknown'
                    ),
                    exc=exc
                )

        # Ensure the dialog is modal
        parent_window = dialog.master
        parent_window.update_idletasks()
        dialog.grab_set()

        # Disable resizing
        if not resizable:
            dialog.resizable(False, False)

        # Close dialog and show the window
        dialog.protocol(
            'WM_DELETE_WINDOW',
            lambda: UIHelper.close_dialog(dialog)
        )

        # Hide the window
        parent_window.withdraw()

        # Give the dialog focus
        dialog.lift()
        dialog.attributes('-topmost', True)
        dialog.after_idle(dialog.attributes, '-topmost', False)
        dialog.focus_set()

        UIHelper.center_window(
            window=dialog,
            width=width,
            height=height
        )

    @staticmethod
    def close_dialog(
        dialog: Wm
    ):
        """Close dialog"""

        # Give the window focus
        parent_window = dialog.master
        parent_window.deiconify()
        parent_window.focus_set()

        # Close dialog
        dialog.destroy()

    @staticmethod
    def count_monitors():
        """Count monitors"""

        return len(screeninfo.get_monitors())
