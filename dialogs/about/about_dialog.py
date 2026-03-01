#!/usr/bin/python3
"""Dialog to show about for the application"""

import os
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk

from tkinter import messagebox
import webbrowser

import requests

from dialogs.waiting.waiting_dialog import WaitingDialog
from libraries.constants.constants import Constants
from libraries.context.context import Context
from libraries.logging.logging_helper import LoggingHelper
from libraries.ui.ui_helper import UIHelper


class AboutDialog:
    """Dialog to show about for the application"""

    def __init__(
        self,
        parent
    ):
        """Initialize dialog"""

        self.__exe_asset = None

        # Create dialog
        self.dialog = UIHelper.create_dialog(parent)

        # Fix dialog's title
        self.dialog.title(Context.get_text('about'))

        # Image
        self.__logo = tk.PhotoImage(
            file=os.path.join(
                Context.get_base_path(),
                Constants.RESOURCES_PATH,
                'img',
                'pincab_manager.png'
            )
        ).subsample(2, 2)
        logo_label = tk.Label(
            self.dialog,
            image=self.__logo
        )
        logo_label.pack(pady=(0, 10))

        # Name + Version
        label_app = tk.Label(
            self.dialog,
            text=f"{Context.get_text('title')} ({Context.get_app_version()})"
        )
        label_app.pack()

        label_dev = tk.Label(
            self.dialog,
            text=f"{Context.get_text('developed_by')}"
        )
        label_dev.pack(pady=(0, 20))

        # Button to check update
        if Context.is_packaged():
            update_button = tk.Button(
                self.dialog,
                text=Context.get_text('update_title'),
                command=self.check_update
            )
            update_button.pack(pady=(0, 20))

        # Social networks
        links = {
            "YouTube": "https://www.youtube.com/@jaylooty_official",
            "Twitch": "https://twitch.tv/jaylooty_official",
            "Discord": "https://discord.gg/ArBfCRCA",
            "GitHub": "https://github.com/JayLooty"
        }

        for name, url in links.items():
            link = tk.Label(
                self.dialog,
                text=name,
                fg="blue",
                cursor="hand2",
                font=("Arial", 11, "underline")
            )
            link.pack()
            link.bind("<Button-1>", lambda e, url=url: webbrowser.open(url))

        donate_button = tk.Button(
            self.dialog,
            text="Donate",
            command=lambda: webbrowser.open(
                "https://own3d.pro/fr/u/jay_looty/tip"),
            font=("Arial", 12, "bold")
        )
        donate_button.pack(pady=20)

        # Fix dialog's size and position
        UIHelper.center_dialog(
            dialog=self.dialog,
            width=600,
            height=500
        )

    def check_update(self):
        """Check GitHub latest release"""
        try:
            repo = "pincab-manager/pincab-manager"
            url = f"https://api.github.com/repos/{repo}/releases/latest"
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json()

            # Check if latest version already used
            latest_version = data["tag_name"].lstrip("v")
            current_version = Context.get_app_version()
            if latest_version == current_version:
                messagebox.showinfo(
                    Context.get_text('info'),
                    Context.get_text(
                        'update_latest_version_used',
                        latest_version=latest_version
                    ),
                    parent=self.dialog
                )
                return

            # Ask confirmation to update
            answer = messagebox.askyesno(
                Context.get_text('question'),
                Context.get_text(
                    'question_update',
                    current_version=current_version,
                    latest_version=latest_version
                ).replace('\\n', '\n'),
                parent=self.dialog
            )
            if not answer:
                return

            # Download the first executable found in assets
            assets = data.get("assets", [])
            self.__exe_asset = next(
                (a for a in assets if a["name"].endswith(".exe")), None)
            if not self.__exe_asset:
                messagebox.showerror(
                    title=Context.get_text('error_title'),
                    message=Context.get_text('error_no_executable_found'),
                    parent=self.dialog
                )
                return

            # Execute the update in a waiting dialog
            WaitingDialog(
                parent=self.dialog.winfo_toplevel(),
                process_name=Context.get_text('process_update'),
                process_function=self.__run_update
            )
        except Exception as exc:
            LoggingHelper.log_error(
                message=Context.get_text(
                    'error_unknown'
                ),
                exc=exc
            )
            messagebox.showerror(
                title=Context.get_text('error_title'),
                message=Context.get_text('error_message'),
                parent=self.dialog
            )

    def __run_update(self, should_interrupt):
        """Run update"""

        # pylint: disable=unused-argument

        download_url = self.__exe_asset["browser_download_url"]
        download_exe_name = self.__exe_asset["name"]

        # Download executable in a temporary file
        temp_dir = tempfile.gettempdir()
        temp_exe_path = os.path.join(temp_dir, download_exe_name)
        with requests.get(
            download_url,
            stream=True,
            timeout=5
        ) as req:
            req.raise_for_status()
            with open(temp_exe_path, 'wb') as f:
                shutil.copyfileobj(req.raw, f)

        # Retrieve current executable
        current_exe_path = sys.executable
        temp_dir = tempfile.gettempdir()
        batch_path = os.path.join(temp_dir, "do_update.bat")
        batch_script = f"""@echo off
echo [Updater] Waiting for the process to close...
timeout /t 2 /nobreak >nul

echo [Updater] Replacing executable...
copy /Y "{temp_exe_path}" "{current_exe_path}"

echo [Updater] Done.
exit
"""

        with open(batch_path, "w", encoding="utf-8") as f:
            f.write(batch_script)

        # pylint: disable=consider-using-with

        # Execute batch in a new console
        subprocess.Popen(['cmd', '/c', 'start', '', batch_path])

        # Kill the application
        os._exit(0)
