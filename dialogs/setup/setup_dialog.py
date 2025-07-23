#!/usr/bin/python3
"""Dialog to setup the application"""

import configparser
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from libraries.constants.constants import Constants, Emulator, Media
from libraries.context.context import Context
from libraries.ui.ui_helper import UIHelper

# pylint: disable=attribute-defined-outside-init, too-many-locals
# pylint: disable=too-many-instance-attributes, too-many-statements
# pylint: disable=too-many-lines, too-many-branches


class SetupDialog:
    """Dialog to setup the application"""

    def __init__(
        self,
        parent,
        callback: any
    ):
        """Initialize dialog"""

        self.__callback = callback
        self.__loaded = False
        self.__lang_code = Context.get_lang_code()

        # Create dialog
        self.dialog = tk.Toplevel(parent)

        # Fix dialog's size and position
        UIHelper.center_dialog(
            dialog=self.dialog,
            width=800,
            height=900
        )

        # Create top frame
        self.top_frame = tk.Frame(
            self.dialog
        )
        self.top_frame.pack(
            side=tk.TOP,
            fill=tk.BOTH,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_BIG
        )

        # Create center frame
        self.center_frame = tk.Frame(
            self.dialog
        )
        self.center_frame.pack(
            side=tk.TOP,
            fill=tk.BOTH,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_BIG
        )

        # Create bottom frame
        self.bottom_frame = tk.Frame(
            self.dialog
        )
        self.bottom_frame.pack(
            side=tk.TOP,
            fill=tk.BOTH,
            expand=True,
            padx=Constants.UI_PAD_SMALL
        )

        # Create components
        self.__create_general_components()
        self.__create_emulators_components()
        self.__create_media_components()
        self.__create_buttons_components()

        # Update texts in UI Components
        self.__update_ui_components_texts()

        self.__loaded = True

        # Update screen about entry changed
        self.__on_entry_changed(None)

    def __browse_folder(
        self,
        entry_folder
    ):
        """Browse folder"""

        folder_selected = filedialog.askdirectory(
            parent=self.dialog
        )
        if folder_selected:
            # Clear current text in the entry
            entry_folder.delete(0, tk.END)
            # Insert the selected folder
            entry_folder.insert(0, folder_selected)

    def __validate(self):
        """Validate"""

        # Retrieve general setup
        pinup_path = self.entry_pinup_path.get()
        simulated = self.simulation_boolean_var.get()
        auto_refresh = self.auto_refresh_boolean_var.get()
        monitor = int(self.combo_monitor.get()) - 1

        # Retrieve emulators setup
        available_emulators = []
        if self.emulator_vpx_boolean_var.get():
            available_emulators.append(Emulator.VISUAL_PINBALL_X.value)
        if self.emulator_fx2_boolean_var.get():
            available_emulators.append(Emulator.PINBALL_FX2.value)
        if self.emulator_fx3_boolean_var.get():
            available_emulators.append(Emulator.PINBALL_FX3.value)
        if self.emulator_fx_boolean_var.get():
            available_emulators.append(Emulator.PINBALL_FX.value)
        if self.emulator_m_boolean_var.get():
            available_emulators.append(Emulator.PINBALL_M.value)
        if self.emulator_fp_boolean_var.get():
            available_emulators.append(Emulator.FUTURE_PINBALL.value)

        # Retrieve media selecting setup
        available_media = []
        if self.media_topper_boolean_var.get():
            available_media.append(Media.TOPPER.value)
        if self.media_backglass_boolean_var.get():
            available_media.append(Media.BACKGLASS.value)
        if self.media_full_dmd_boolean_var.get():
            available_media.append(Media.FULL_DMD.value)
        if self.media_playfield_boolean_var.get():
            available_media.append(Media.PLAYFIELD.value)
        if self.media_audio_boolean_var.get():
            available_media.append(Media.AUDIO.value)
        if self.media_dmd_boolean_var.get():
            available_media.append(Media.DMD.value)
        if self.media_flyer_boolean_var.get():
            available_media.append(Media.FLYER.value)
        if self.media_help_boolean_var.get():
            available_media.append(Media.HELP.value)
        if self.media_other_boolean_var.get():
            available_media.append(Media.OTHER.value)
        if self.media_wheel_bar_boolean_var.get():
            available_media.append(Media.WHEEL_BAR.value)
        if self.media_wheel_image_boolean_var.get():
            available_media.append(Media.WHEEL_IMAGE.value)

        # Retrieve screen numbers media setup
        screen_number_by_media = {}
        for media in Media:
            screen_number = -1
            match media:
                case Media.TOPPER:
                    if self.media_screen_number_topper_combo.current() > 0:
                        screen_number = \
                            self.media_screen_number_topper_combo.current() - 1
                case Media.BACKGLASS:
                    if self.media_screen_number_backglass_combo.current() > 0:
                        screen_number = \
                            self.media_screen_number_backglass_combo.current() - 1
                case Media.FULL_DMD:
                    if self.media_screen_number_full_dmd_combo.current() > 0:
                        screen_number = \
                            self.media_screen_number_full_dmd_combo.current() - 1
                case Media.PLAYFIELD:
                    if self.media_screen_number_playfield_combo.current() > 0:
                        screen_number = \
                            self.media_screen_number_playfield_combo.current() - 1
            screen_number_by_media[media.value] = screen_number

        # Save setup in a cfg file
        setup = configparser.ConfigParser()
        setup['DEFAULT'] = {
            Constants.SETUP_LANG_CODE: self.__lang_code,
            Constants.SETUP_PINUP_PATH: pinup_path,
            Constants.SETUP_MONITOR: monitor,
            Constants.SETUP_SIMULATED: simulated,
            Constants.SETUP_AUTO_REFRESH: auto_refresh,
            Constants.SETUP_AVAILABLE_EMULATORS: available_emulators,
            Constants.SETUP_AVAILABLE_MEDIA: available_media,
            Constants.SETUP_SCREEN_NUMBER_BY_MEDIA: screen_number_by_media
        }

        if self.emulator_vpx_boolean_var.get():
            setup['DEFAULT'][Constants.SETUP_VPX_PATH] = self.entry_emulator_vpx_path.get()

        if self.emulator_fp_boolean_var.get():
            setup['DEFAULT'][Constants.SETUP_FP_PATH] = self.entry_emulator_fp_path.get()

        if self.emulator_fx2_boolean_var.get() or \
                self.emulator_fx3_boolean_var.get() or \
                self.emulator_fx_boolean_var.get() or \
                self.emulator_m_boolean_var.get():
            setup['DEFAULT'][Constants.SETUP_STEAM_PATH] = self.entry_emulator_steam_path.get()

        setup_file_path = Context.get_setup_file_path()
        setup_file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(
            setup_file_path,
            mode='w',
            encoding='UTF-8'
        ) as file:
            setup.write(file)

        # Update context from setup
        Context.update_context_from_setup()

        # Close the dialog after validation
        UIHelper.close_dialog(self.dialog)

        # Call back
        self.__callback()

    def __cancel(self):
        """Cancel"""

        # Close the dialog without saving
        UIHelper.close_dialog(self.dialog)

    def __on_entry_changed(self, *args):
        """Called when an entry changed"""

        if not self.__loaded:
            return

        # Reload UI Texts if the source is the combo lang
        try:
            widget = args[0].widget
            if widget == self.combo_lang:
                self.__lang_code = 'en'
                if self.combo_lang.get() == Context.get_text('lang_fr'):
                    self.__lang_code = 'fr'

                # Update texts in UI Components
                self.__update_ui_components_texts()
        except Exception:
            pass

        # Show/Hide components for VPX's Path
        if self.emulator_vpx_boolean_var.get():
            self.emulator_vpx_path_frame.pack(
                side=tk.RIGHT,
                padx=Constants.UI_PAD_SMALL
            )
        else:
            self.emulator_vpx_path_frame.pack_forget()
            self.entry_emulator_vpx_path_var.set('')

        # Show/Hide components for FUTURE_PINBALL's Path
        if self.emulator_fp_boolean_var.get():
            self.emulator_fp_path_frame.pack(
                side=tk.RIGHT,
                padx=Constants.UI_PAD_SMALL
            )
        else:
            self.emulator_fp_path_frame.pack_forget()
            self.entry_emulator_fp_path_var.set('')

        # Show/Hide components for STEAM's Path
        if self.emulator_fx2_boolean_var.get() or \
                self.emulator_fx3_boolean_var.get() or \
                self.emulator_fx_boolean_var.get() or \
                self.emulator_m_boolean_var.get():
            self.emulator_steam_path_frame.pack(
                side=tk.RIGHT,
                padx=Constants.UI_PAD_SMALL
            )
        else:
            self.emulator_steam_path_frame.pack_forget()
            self.entry_emulator_steam_path_var.set('')

        # Show/Hide components for TOPPER's Screen Number
        if self.media_topper_boolean_var.get():
            self.media_screen_number_topper_frame.pack(
                side=tk.RIGHT,
                padx=Constants.UI_PAD_SMALL
            )
        else:
            self.media_screen_number_topper_frame.pack_forget()
            self.media_screen_number_topper_combo.set('N/A')

        # Show/Hide components for BACKGLASS's Screen Number
        if self.media_backglass_boolean_var.get():
            self.media_screen_number_backglass_frame.pack(
                side=tk.RIGHT,
                padx=Constants.UI_PAD_SMALL
            )
        else:
            self.media_screen_number_backglass_frame.pack_forget()
            self.media_screen_number_backglass_combo.set('N/A')

        # Show/Hide components for FULL_DMD's Screen Number
        if self.media_full_dmd_boolean_var.get():
            self.media_screen_number_full_dmd_frame.pack(
                side=tk.RIGHT,
                padx=Constants.UI_PAD_SMALL
            )
        else:
            self.media_screen_number_full_dmd_frame.pack_forget()
            self.media_screen_number_full_dmd_combo.set('N/A')

        # Show/Hide components for PLAYFIELD's Screen Number
        if self.media_playfield_boolean_var.get():
            self.media_screen_number_playfield_frame.pack(
                side=tk.RIGHT,
                padx=Constants.UI_PAD_SMALL
            )
        else:
            self.media_screen_number_playfield_frame.pack_forget()
            self.media_screen_number_playfield_combo.set('N/A')

        # Enable/Disable button to validate
        validate_enabled = True

        if len(self.entry_pinup_path_var.get()) == 0 or \
                not Path(self.entry_pinup_path_var.get()).exists():
            validate_enabled = False

        if self.emulator_vpx_boolean_var.get():
            if len(self.entry_emulator_vpx_path_var.get()) == 0 or \
                    not Path(self.entry_emulator_vpx_path_var.get()).exists():
                validate_enabled = False

        if self.emulator_fp_boolean_var.get():
            if len(self.entry_emulator_fp_path_var.get()) == 0 or \
                    not Path(self.entry_emulator_fp_path_var.get()).exists():
                validate_enabled = False

        if self.emulator_fx2_boolean_var.get() or \
                self.emulator_fx3_boolean_var.get() or \
                self.emulator_fx_boolean_var.get() or \
                self.emulator_m_boolean_var.get():
            if len(self.entry_emulator_steam_path_var.get()) == 0 or \
                    not Path(self.entry_emulator_steam_path_var.get()).exists():
                validate_enabled = False

        if validate_enabled:
            self.button_validate.config(state=tk.NORMAL)
        else:
            self.button_validate.config(state=tk.DISABLED)

    def __create_general_components(self):
        """Create general components"""

        # Create frame
        self.general_frame = tk.LabelFrame(
            self.top_frame
        )
        self.general_frame.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=Constants.UI_PAD_SMALL
        )

        # Create Combobox for language
        lang_frame = tk.Frame(self.general_frame)
        lang_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            pady=Constants.UI_PAD_SMALL
        )
        self.label_lang = tk.Label(
            lang_frame
        )
        self.label_lang.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.combo_lang = ttk.Combobox(
            lang_frame,
            values=[]
        )
        self.combo_lang.config(state="readonly")
        self.combo_lang.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.combo_lang.bind(
            "<<ComboboxSelected>>",
            self.__on_entry_changed
        )

        # Create folder PINUP selection
        pinup_path_frame = tk.Frame(self.general_frame)
        pinup_path_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            pady=Constants.UI_PAD_SMALL
        )
        self.label_pinup_path = tk.Label(
            pinup_path_frame
        )
        self.label_pinup_path.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.entry_pinup_path_var = tk.StringVar()
        self.entry_pinup_path_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.entry_pinup_path = tk.Entry(
            pinup_path_frame,
            textvariable=self.entry_pinup_path_var,
            width=40
        )
        self.entry_pinup_path.insert(
            0,
            Context.get_pinup_path()
        )
        self.entry_pinup_path.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.button_browse_vpinball = tk.Button(
            pinup_path_frame,
            command=lambda: self.__browse_folder(self.entry_pinup_path)
        )
        self.button_browse_vpinball.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )

        # Create Combobox for monitor
        monitor_frame = tk.Frame(self.general_frame)
        monitor_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            pady=Constants.UI_PAD_SMALL
        )
        self.label_monitor = tk.Label(
            monitor_frame
        )
        self.label_monitor.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.combo_monitor = ttk.Combobox(
            monitor_frame,
            values=list(range(1, UIHelper.count_monitors() + 1))
        )
        self.combo_monitor.set(
            Context.get_monitor() + 1
        )
        self.combo_monitor.config(state="readonly")
        self.combo_monitor.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.combo_monitor.bind(
            "<<ComboboxSelected>>",
            self.__on_entry_changed
        )

        # Create simulation checkbox
        simulation_frame = tk.Frame(self.general_frame)
        simulation_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.simulation_boolean_var = tk.BooleanVar()
        self.simulation_boolean_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.simulation_boolean_var.set(
            Context.is_simulated()
        )
        simulation_checkbox = tk.Checkbutton(
            simulation_frame,
            variable=self.simulation_boolean_var
        )
        simulation_checkbox.pack(
            side=tk.LEFT,
        )
        self.label_simulation = tk.Label(
            simulation_frame
        )
        self.label_simulation.pack(
            side=tk.LEFT
        )
        self.label_simulation.bind(
            "<Button-1>",
            lambda e: simulation_checkbox.invoke()
        )

        # Create auto refresh checkbox
        auto_refresh_frame = tk.Frame(self.general_frame)
        auto_refresh_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.auto_refresh_boolean_var = tk.BooleanVar()
        self.auto_refresh_boolean_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.auto_refresh_boolean_var.set(
            Context.is_auto_refresh()
        )
        auto_refresh_checkbox = tk.Checkbutton(
            auto_refresh_frame,
            variable=self.auto_refresh_boolean_var
        )
        auto_refresh_checkbox.pack(
            side=tk.LEFT,
        )
        self.label_auto_refresh = tk.Label(
            auto_refresh_frame
        )
        self.label_auto_refresh.pack(
            side=tk.LEFT
        )
        self.label_auto_refresh.bind(
            "<Button-1>",
            lambda e: auto_refresh_checkbox.invoke()
        )

    def __create_emulators_components(self):
        """Create emulators components"""

        # Create frame
        self.emulators_frame = tk.LabelFrame(
            self.center_frame
        )
        self.emulators_frame.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=Constants.UI_PAD_SMALL
        )

        # Create frame for emulator VISUAL_PINBALL_X
        current_emulator = Emulator.VISUAL_PINBALL_X
        emulator_vpx_frame = tk.Frame(self.emulators_frame)
        emulator_vpx_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.emulator_vpx_boolean_var = tk.BooleanVar()
        self.emulator_vpx_boolean_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.emulator_vpx_boolean_var.set(
            current_emulator.value in Context.list_available_emulators()
        )
        emulator_vpx_checkbox = tk.Checkbutton(
            emulator_vpx_frame,
            variable=self.emulator_vpx_boolean_var
        )
        emulator_vpx_checkbox.pack(
            side=tk.LEFT
        )
        emulator_vpx_label = tk.Label(
            emulator_vpx_frame,
            text=current_emulator.value
        )
        emulator_vpx_label.pack(
            side=tk.LEFT
        )
        emulator_vpx_label.bind(
            "<Button-1>",
            lambda e: emulator_vpx_checkbox.invoke()
        )
        self.emulator_vpx_path_frame = tk.Frame(
            emulator_vpx_frame
        )
        self.emulator_vpx_path_frame.pack(
            side=tk.RIGHT,
            padx=Constants.UI_PAD_SMALL
        )
        self.label_emulator_vpx_path = tk.Label(
            self.emulator_vpx_path_frame,
        )
        self.label_emulator_vpx_path.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.entry_emulator_vpx_path_var = tk.StringVar()
        self.entry_emulator_vpx_path_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.entry_emulator_vpx_path = tk.Entry(
            self.emulator_vpx_path_frame,
            textvariable=self.entry_emulator_vpx_path_var,
            width=40
        )
        self.entry_emulator_vpx_path.insert(
            0,
            Context.get_emulator_path(current_emulator)
        )
        self.entry_emulator_vpx_path.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.button_browse_emulator_vpx_path = tk.Button(
            self.emulator_vpx_path_frame,
            command=lambda: self.__browse_folder(self.entry_emulator_vpx_path)
        )
        self.button_browse_emulator_vpx_path.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )

        # Create frame for emulator FUTURE_PINBALL
        current_emulator = Emulator.FUTURE_PINBALL
        emulator_fp_frame = tk.Frame(self.emulators_frame)
        emulator_fp_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.emulator_fp_boolean_var = tk.BooleanVar()
        self.emulator_fp_boolean_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.emulator_fp_boolean_var.set(
            current_emulator.value in Context.list_available_emulators()
        )
        emulator_fp_checkbox = tk.Checkbutton(
            emulator_fp_frame,
            variable=self.emulator_fp_boolean_var
        )
        emulator_fp_checkbox.pack(
            side=tk.LEFT
        )
        emulator_fp_label = tk.Label(
            emulator_fp_frame,
            text=current_emulator.value
        )
        emulator_fp_label.pack(
            side=tk.LEFT
        )
        emulator_fp_label.bind(
            "<Button-1>",
            lambda e: emulator_fp_checkbox.invoke()
        )
        self.emulator_fp_path_frame = tk.Frame(
            emulator_fp_frame
        )
        self.emulator_fp_path_frame.pack(
            side=tk.RIGHT,
            padx=Constants.UI_PAD_SMALL
        )
        self.label_emulator_fp_path = tk.Label(
            self.emulator_fp_path_frame
        )
        self.label_emulator_fp_path.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.entry_emulator_fp_path_var = tk.StringVar()
        self.entry_emulator_fp_path_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.entry_emulator_fp_path = tk.Entry(
            self.emulator_fp_path_frame,
            textvariable=self.entry_emulator_fp_path_var,
            width=40
        )
        self.entry_emulator_fp_path.insert(
            0,
            Context.get_emulator_path(current_emulator)
        )
        self.entry_emulator_fp_path.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.button_browse_emulator_fp_path = tk.Button(
            self.emulator_fp_path_frame,
            command=lambda: self.__browse_folder(self.entry_emulator_fp_path)
        )
        self.button_browse_emulator_fp_path.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )

        # Create frame for emulator PINBALL_FX2
        current_emulator = Emulator.PINBALL_FX2
        emulator_fx2_frame = tk.Frame(self.emulators_frame)
        emulator_fx2_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.emulator_fx2_boolean_var = tk.BooleanVar()
        self.emulator_fx2_boolean_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.emulator_fx2_boolean_var.set(
            current_emulator.value in Context.list_available_emulators()
        )
        emulator_fx2_checkbox = tk.Checkbutton(
            emulator_fx2_frame,
            variable=self.emulator_fx2_boolean_var
        )
        emulator_fx2_checkbox.pack(
            side=tk.LEFT
        )
        emulator_fx2_label = tk.Label(
            emulator_fx2_frame,
            text=current_emulator.value
        )
        emulator_fx2_label.pack(
            side=tk.LEFT
        )
        emulator_fx2_label.bind(
            "<Button-1>",
            lambda e: emulator_fx2_checkbox.invoke()
        )
        self.emulator_steam_path_frame = tk.Frame(
            emulator_fx2_frame
        )
        self.emulator_steam_path_frame.pack(
            side=tk.RIGHT,
            padx=Constants.UI_PAD_SMALL
        )
        self.label_emulator_steam_path = tk.Label(
            self.emulator_steam_path_frame
        )
        self.label_emulator_steam_path.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.entry_emulator_steam_path_var = tk.StringVar()
        self.entry_emulator_steam_path_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.entry_emulator_steam_path = tk.Entry(
            self.emulator_steam_path_frame,
            textvariable=self.entry_emulator_steam_path_var,
            width=40
        )
        self.entry_emulator_steam_path.insert(
            0,
            Context.get_steam_path()
        )
        self.entry_emulator_steam_path.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )
        self.button_browse_emulator_steam_path = tk.Button(
            self.emulator_steam_path_frame,
            command=lambda: self.__browse_folder(
                self.entry_emulator_steam_path)
        )
        self.button_browse_emulator_steam_path.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )

        # Create frame for emulator PINBALL_FX3
        current_emulator = Emulator.PINBALL_FX3
        emulator_fx3_frame = tk.Frame(self.emulators_frame)
        emulator_fx3_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.emulator_fx3_boolean_var = tk.BooleanVar()
        self.emulator_fx3_boolean_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.emulator_fx3_boolean_var.set(
            current_emulator.value in Context.list_available_emulators()
        )
        emulator_fx3_checkbox = tk.Checkbutton(
            emulator_fx3_frame,
            variable=self.emulator_fx3_boolean_var
        )
        emulator_fx3_checkbox.pack(
            side=tk.LEFT
        )
        emulator_fx3_label = tk.Label(
            emulator_fx3_frame,
            text=current_emulator.value
        )
        emulator_fx3_label.pack(
            side=tk.LEFT
        )
        emulator_fx3_label.bind(
            "<Button-1>",
            lambda e: emulator_fx3_checkbox.invoke()
        )

        # Create frame for emulator PINBALL_FX
        current_emulator = Emulator.PINBALL_FX
        emulator_fx_frame = tk.Frame(self.emulators_frame)
        emulator_fx_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.emulator_fx_boolean_var = tk.BooleanVar()
        self.emulator_fx_boolean_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.emulator_fx_boolean_var.set(
            current_emulator.value in Context.list_available_emulators()
        )
        emulator_fx_checkbox = tk.Checkbutton(
            emulator_fx_frame,
            variable=self.emulator_fx_boolean_var
        )
        emulator_fx_checkbox.pack(
            side=tk.LEFT
        )
        emulator_fx_label = tk.Label(
            emulator_fx_frame,
            text=current_emulator.value
        )
        emulator_fx_label.pack(
            side=tk.LEFT
        )
        emulator_fx_label.bind(
            "<Button-1>",
            lambda e: emulator_fx_checkbox.invoke()
        )

        # Create frame for emulator PINBALL_M
        current_emulator = Emulator.PINBALL_M
        emulator_m_frame = tk.Frame(self.emulators_frame)
        emulator_m_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.emulator_m_boolean_var = tk.BooleanVar()
        self.emulator_m_boolean_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.emulator_m_boolean_var.set(
            current_emulator.value in Context.list_available_emulators()
        )
        emulator_m_checkbox = tk.Checkbutton(
            emulator_m_frame,
            variable=self.emulator_m_boolean_var
        )
        emulator_m_checkbox.pack(
            side=tk.LEFT
        )
        emulator_m_label = tk.Label(
            emulator_m_frame,
            text=current_emulator.value
        )
        emulator_m_label.pack(
            side=tk.LEFT
        )
        emulator_m_label.bind(
            "<Button-1>",
            lambda e: emulator_m_checkbox.invoke()
        )

    def __create_media_components(self):
        """Create media components"""

        # Initialize screen numbers values
        screen_numbers_values = [
            'N/A',
            '0',
            '1',
            '2',
            '3',
            '4',
            '5',
            '6',
            '7',
            '8',
            '9'
        ]

        # Create frame for all media
        self.media_frame = tk.LabelFrame(
            self.bottom_frame
        )
        self.media_frame.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=Constants.UI_PAD_SMALL
        )

        # Create frame for media TOPPER
        current_media = Media.TOPPER
        media_topper_frame = tk.Frame(self.media_frame)
        media_topper_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.media_topper_boolean_var = tk.BooleanVar()
        self.media_topper_boolean_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.media_topper_boolean_var.set(
            current_media.value in Context.list_available_media()
        )
        media_topper_checkbox = tk.Checkbutton(
            media_topper_frame,
            variable=self.media_topper_boolean_var
        )
        media_topper_checkbox.pack(
            side=tk.LEFT
        )
        self.media_topper_label = tk.Label(
            media_topper_frame
        )
        self.media_topper_label.pack(
            side=tk.LEFT
        )
        self.media_topper_label.bind(
            "<Button-1>",
            lambda e: media_topper_checkbox.invoke()
        )
        self.media_screen_number_topper_frame = tk.Frame(
            media_topper_frame
        )
        self.media_screen_number_topper_frame.pack(
            side=tk.RIGHT,
            padx=Constants.UI_PAD_SMALL
        )
        self.media_screen_number_topper_combo = ttk.Combobox(
            self.media_screen_number_topper_frame,
            values=screen_numbers_values
        )
        if current_media.value in Context.get_screen_number_by_media() \
                and Context.get_screen_number_by_media()[current_media.value] >= 0:
            self.media_screen_number_topper_combo.set(
                value=screen_numbers_values[Context.get_screen_number_by_media()[
                    current_media.value] + 1]
            )
        else:
            self.media_screen_number_topper_combo.set(
                value=screen_numbers_values[0]
            )
        self.media_screen_number_topper_combo.config(state="readonly")
        self.media_screen_number_topper_combo.bind(
            "<<ComboboxSelected>>",
            self.__on_entry_changed
        )
        self.media_screen_number_topper_combo.pack(
            side=tk.RIGHT,
            padx=Constants.UI_PAD_SMALL
        )
        self.media_screen_number_topper_label = tk.Label(
            self.media_screen_number_topper_frame
        )
        self.media_screen_number_topper_label.pack(
            side=tk.RIGHT
        )

        # Create frame for media BACKGLASS
        current_media = Media.BACKGLASS
        media_backglass_frame = tk.Frame(self.media_frame)
        media_backglass_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.media_backglass_boolean_var = tk.BooleanVar()
        self.media_backglass_boolean_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.media_backglass_boolean_var.set(
            current_media.value in Context.list_available_media()
        )
        media_backglass_checkbox = tk.Checkbutton(
            media_backglass_frame,
            variable=self.media_backglass_boolean_var
        )
        media_backglass_checkbox.pack(
            side=tk.LEFT
        )
        self.media_backglass_label = tk.Label(
            media_backglass_frame,
        )
        self.media_backglass_label.pack(
            side=tk.LEFT
        )
        self.media_backglass_label.bind(
            "<Button-1>",
            lambda e: media_backglass_checkbox.invoke()
        )
        self.media_screen_number_backglass_frame = tk.Frame(
            media_backglass_frame
        )
        self.media_screen_number_backglass_frame.pack(
            side=tk.RIGHT,
            padx=Constants.UI_PAD_SMALL
        )
        self.media_screen_number_backglass_combo = ttk.Combobox(
            self.media_screen_number_backglass_frame,
            values=screen_numbers_values
        )
        if current_media.value in Context.get_screen_number_by_media() \
                and Context.get_screen_number_by_media()[current_media.value] >= 0:
            self.media_screen_number_backglass_combo.set(
                value=screen_numbers_values[Context.get_screen_number_by_media()[
                    current_media.value] + 1]
            )
        else:
            self.media_screen_number_backglass_combo.set(
                value=screen_numbers_values[0]
            )
        self.media_screen_number_backglass_combo.config(
            state="readonly")
        self.media_screen_number_backglass_combo.bind(
            "<<ComboboxSelected>>",
            self.__on_entry_changed
        )
        self.media_screen_number_backglass_combo.pack(
            side=tk.RIGHT,
            padx=Constants.UI_PAD_SMALL
        )
        self.media_screen_number_backglass_label = tk.Label(
            self.media_screen_number_backglass_frame
        )
        self.media_screen_number_backglass_label.pack(
            side=tk.RIGHT
        )

        # Create frame for media FULL_DMD
        current_media = Media.FULL_DMD
        media_full_dmd_frame = tk.Frame(self.media_frame)
        media_full_dmd_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.media_full_dmd_boolean_var = tk.BooleanVar()
        self.media_full_dmd_boolean_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.media_full_dmd_boolean_var.set(
            current_media.value in Context.list_available_media()
        )
        media_full_dmd_checkbox = tk.Checkbutton(
            media_full_dmd_frame,
            variable=self.media_full_dmd_boolean_var
        )
        media_full_dmd_checkbox.pack(
            side=tk.LEFT
        )
        self.media_full_dmd_label = tk.Label(
            media_full_dmd_frame
        )
        self.media_full_dmd_label.pack(
            side=tk.LEFT
        )
        self.media_full_dmd_label.bind(
            "<Button-1>",
            lambda e: media_full_dmd_checkbox.invoke()
        )
        self.media_screen_number_full_dmd_frame = tk.Frame(
            media_full_dmd_frame
        )
        self.media_screen_number_full_dmd_frame.pack(
            side=tk.RIGHT,
            padx=Constants.UI_PAD_SMALL
        )
        self.media_screen_number_full_dmd_combo = ttk.Combobox(
            self.media_screen_number_full_dmd_frame,
            values=screen_numbers_values
        )
        if current_media.value in Context.get_screen_number_by_media() \
                and Context.get_screen_number_by_media()[current_media.value] >= 0:
            self.media_screen_number_full_dmd_combo.set(
                value=screen_numbers_values[Context.get_screen_number_by_media()[
                    current_media.value] + 1]
            )
        else:
            self.media_screen_number_full_dmd_combo.set(
                value=screen_numbers_values[0]
            )
        self.media_screen_number_full_dmd_combo.config(state="readonly")
        self.media_screen_number_full_dmd_combo.bind(
            "<<ComboboxSelected>>",
            self.__on_entry_changed
        )
        self.media_screen_number_full_dmd_combo.pack(
            side=tk.RIGHT,
            padx=Constants.UI_PAD_SMALL
        )
        self.media_screen_number_full_dmd_label = tk.Label(
            self.media_screen_number_full_dmd_frame
        )
        self.media_screen_number_full_dmd_label.pack(
            side=tk.RIGHT
        )

        # Create frame for media PLAYFIELD
        current_media = Media.PLAYFIELD
        media_playfield_frame = tk.Frame(self.media_frame)
        media_playfield_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.media_playfield_boolean_var = tk.BooleanVar()
        self.media_playfield_boolean_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.media_playfield_boolean_var.set(
            current_media.value in Context.list_available_media()
        )
        media_playfield_checkbox = tk.Checkbutton(
            media_playfield_frame,
            variable=self.media_playfield_boolean_var
        )
        media_playfield_checkbox.pack(
            side=tk.LEFT
        )
        self.media_playfield_label = tk.Label(
            media_playfield_frame
        )
        self.media_playfield_label.pack(
            side=tk.LEFT
        )
        self.media_playfield_label.bind(
            "<Button-1>",
            lambda e: media_playfield_checkbox.invoke()
        )
        self.media_screen_number_playfield_frame = tk.Frame(
            media_playfield_frame
        )
        self.media_screen_number_playfield_frame.pack(
            side=tk.RIGHT,
            padx=Constants.UI_PAD_SMALL
        )
        self.media_screen_number_playfield_combo = ttk.Combobox(
            self.media_screen_number_playfield_frame,
            values=screen_numbers_values
        )
        if current_media.value in Context.get_screen_number_by_media() \
                and Context.get_screen_number_by_media()[current_media.value] >= 0:
            self.media_screen_number_playfield_combo.set(
                value=screen_numbers_values[Context.get_screen_number_by_media()[
                    current_media.value] + 1]
            )
        else:
            self.media_screen_number_playfield_combo.set(
                value=screen_numbers_values[0]
            )
        self.media_screen_number_playfield_combo.config(
            state="readonly")
        self.media_screen_number_playfield_combo.bind(
            "<<ComboboxSelected>>",
            self.__on_entry_changed
        )
        self.media_screen_number_playfield_combo.pack(
            side=tk.RIGHT,
            padx=Constants.UI_PAD_SMALL
        )
        self.media_screen_number_playfield_label = tk.Label(
            self.media_screen_number_playfield_frame
        )
        self.media_screen_number_playfield_label.pack(
            side=tk.RIGHT
        )

        # Create frame for media AUDIO
        current_media = Media.AUDIO
        media_audio_frame = tk.Frame(self.media_frame)
        media_audio_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.media_audio_boolean_var = tk.BooleanVar()
        self.media_audio_boolean_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.media_audio_boolean_var.set(
            current_media.value in Context.list_available_media()
        )
        media_audio_checkbox = tk.Checkbutton(
            media_audio_frame,
            variable=self.media_audio_boolean_var
        )
        media_audio_checkbox.pack(
            side=tk.LEFT
        )
        self.media_audio_label = tk.Label(
            media_audio_frame
        )
        self.media_audio_label.pack(
            side=tk.LEFT
        )
        self.media_audio_label.bind(
            "<Button-1>",
            lambda e: media_audio_checkbox.invoke()
        )

        # Create frame for media DMD
        current_media = Media.DMD
        media_dmd_frame = tk.Frame(self.media_frame)
        media_dmd_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.media_dmd_boolean_var = tk.BooleanVar()
        self.media_dmd_boolean_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.media_dmd_boolean_var.set(
            current_media.value in Context.list_available_media()
        )
        media_dmd_checkbox = tk.Checkbutton(
            media_dmd_frame,
            variable=self.media_dmd_boolean_var
        )
        media_dmd_checkbox.pack(
            side=tk.LEFT
        )
        self.media_dmd_label = tk.Label(
            media_dmd_frame
        )
        self.media_dmd_label.pack(
            side=tk.LEFT
        )
        self.media_dmd_label.bind(
            "<Button-1>",
            lambda e: media_dmd_checkbox.invoke()
        )

        # Create frame for media FLYER
        current_media = Media.FLYER
        media_flyer_frame = tk.Frame(self.media_frame)
        media_flyer_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.media_flyer_boolean_var = tk.BooleanVar()
        self.media_flyer_boolean_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.media_flyer_boolean_var.set(
            current_media.value in Context.list_available_media()
        )
        media_flyer_checkbox = tk.Checkbutton(
            media_flyer_frame,
            variable=self.media_flyer_boolean_var
        )
        media_flyer_checkbox.pack(
            side=tk.LEFT
        )
        self.media_flyer_label = tk.Label(
            media_flyer_frame
        )
        self.media_flyer_label.pack(
            side=tk.LEFT
        )
        self.media_flyer_label.bind(
            "<Button-1>",
            lambda e: media_flyer_checkbox.invoke()
        )

        # Create frame for media HELP
        current_media = Media.HELP
        media_help_frame = tk.Frame(self.media_frame)
        media_help_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.media_help_boolean_var = tk.BooleanVar()
        self.media_help_boolean_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.media_help_boolean_var.set(
            current_media.value in Context.list_available_media()
        )
        media_help_checkbox = tk.Checkbutton(
            media_help_frame,
            variable=self.media_help_boolean_var
        )
        media_help_checkbox.pack(
            side=tk.LEFT
        )
        self.media_help_label = tk.Label(
            media_help_frame
        )
        self.media_help_label.pack(
            side=tk.LEFT
        )
        self.media_help_label.bind(
            "<Button-1>",
            lambda e: media_help_checkbox.invoke()
        )

        # Create frame for media OTHER
        current_media = Media.OTHER
        media_other_frame = tk.Frame(self.media_frame)
        media_other_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.media_other_boolean_var = tk.BooleanVar()
        self.media_other_boolean_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.media_other_boolean_var.set(
            current_media.value in Context.list_available_media()
        )
        media_other_checkbox = tk.Checkbutton(
            media_other_frame,
            variable=self.media_other_boolean_var
        )
        media_other_checkbox.pack(
            side=tk.LEFT
        )
        self.media_other_label = tk.Label(
            media_other_frame
        )
        self.media_other_label.pack(
            side=tk.LEFT
        )
        self.media_other_label.bind(
            "<Button-1>",
            lambda e: media_other_checkbox.invoke()
        )

        # Create frame for media WHEEL_BAR
        current_media = Media.WHEEL_BAR
        media_wheel_bar_frame = tk.Frame(self.media_frame)
        media_wheel_bar_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.media_wheel_bar_boolean_var = tk.BooleanVar()
        self.media_wheel_bar_boolean_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.media_wheel_bar_boolean_var.set(
            current_media.value in Context.list_available_media()
        )
        media_wheel_bar_checkbox = tk.Checkbutton(
            media_wheel_bar_frame,
            variable=self.media_wheel_bar_boolean_var
        )
        media_wheel_bar_checkbox.pack(
            side=tk.LEFT
        )
        self.media_wheel_bar_label = tk.Label(
            media_wheel_bar_frame
        )
        self.media_wheel_bar_label.pack(
            side=tk.LEFT
        )
        self.media_wheel_bar_label.bind(
            "<Button-1>",
            lambda e: media_wheel_bar_checkbox.invoke()
        )

        # Create frame for media WHEEL_IMAGE
        current_media = Media.WHEEL_IMAGE
        media_wheel_image_frame = tk.Frame(self.media_frame)
        media_wheel_image_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.media_wheel_image_boolean_var = tk.BooleanVar()
        self.media_wheel_image_boolean_var.trace_add(
            "write",
            self.__on_entry_changed
        )
        self.media_wheel_image_boolean_var.set(
            current_media.value in Context.list_available_media()
        )
        media_wheel_image_checkbox = tk.Checkbutton(
            media_wheel_image_frame,
            variable=self.media_wheel_image_boolean_var
        )
        media_wheel_image_checkbox.pack(
            side=tk.LEFT
        )
        self.media_wheel_image_label = tk.Label(
            media_wheel_image_frame
        )
        self.media_wheel_image_label.pack(
            side=tk.LEFT
        )
        self.media_wheel_image_label.bind(
            "<Button-1>",
            lambda e: media_wheel_image_checkbox.invoke()
        )

    def __create_buttons_components(self):
        """Create bottom components"""

        # Create buttons frame
        buttons_frame = tk.Frame(self.dialog)
        buttons_frame.pack(
            side=tk.BOTTOM,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )

        # Create buttons to cancel and validate
        self.button_cancel = tk.Button(
            buttons_frame,
            command=self.__cancel
        )
        self.button_cancel.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )

        self.button_validate = tk.Button(
            buttons_frame,
            command=self.__validate
        )
        self.button_validate.config(state=tk.DISABLED)
        self.button_validate.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL
        )

    def __update_ui_components_texts(self):
        """Update texts in UI Components"""

        self.dialog.title(Context.get_text(
            'setup',
            lang=self.__lang_code
        ))

        self.label_lang.config(
            text=Context.get_text(
                'lang',
                lang=self.__lang_code
            )
        )

        self.combo_lang.config(
            values=[
                Context.get_text(
                    'lang_fr',
                    lang=self.__lang_code
                ),
                Context.get_text(
                    'lang_en',
                    lang=self.__lang_code
                )
            ]
        )
        self.combo_lang.set(
            Context.get_text(
                f'lang_{self.__lang_code}',
                lang=self.__lang_code
            )
        )

        self.label_pinup_path.config(
            text=Context.get_text(
                'input_folder',
                lang=self.__lang_code,
                target='PinUPSystem'
            )
        )

        self.general_frame.config(
            text=Context.get_text(
                'setup_general',
                lang=self.__lang_code
            )
        )

        self.button_browse_vpinball.config(
            text=Context.get_text(
                'browse',
                lang=self.__lang_code
            )
        )

        self.label_monitor.config(
            text=Context.get_text(
                'monitor',
                lang=self.__lang_code
            )
        )

        self.label_simulation.config(
            text=Context.get_text(
                'simulation',
                lang=self.__lang_code
            )
        )

        self.label_auto_refresh.config(
            text=Context.get_text(
                'auto_refresh',
                lang=self.__lang_code
            )
        )

        self.emulators_frame.config(
            text=Context.get_text(
                'setup_emulators',
                lang=self.__lang_code
            )
        )

        self.label_emulator_vpx_path.config(
            text=Context.get_text(
                'input_folder',
                lang=self.__lang_code,
                target='VisualPinball'
            )
        )

        self.button_browse_emulator_vpx_path.config(
            text=Context.get_text(
                'browse',
                lang=self.__lang_code
            )
        )

        self.label_emulator_fp_path.config(
            text=Context.get_text(
                'input_folder',
                lang=self.__lang_code,
                target='FuturePinball'
            )
        )

        self.button_browse_emulator_fp_path.config(
            text=Context.get_text(
                'browse',
                lang=self.__lang_code
            )
        )

        self.label_emulator_steam_path.config(
            text=Context.get_text(
                'input_folder',
                lang=self.__lang_code,
                target='Steam'
            )
        )

        self.button_browse_emulator_steam_path.config(
            text=Context.get_text(
                'browse',
                lang=self.__lang_code
            )
        )

        self.media_frame.config(
            text=Context.get_text(
                'setup_media',
                lang=self.__lang_code
            )
        )

        self.media_topper_label.config(
            text=Context.get_text(
                Media.TOPPER.value,
                lang=self.__lang_code
            )
        )
        self.media_screen_number_topper_label.config(
            text=Context.get_text(
                'setup_screen_number',
                lang=self.__lang_code
            )
        )

        self.media_backglass_label.config(
            text=Context.get_text(
                Media.BACKGLASS.value,
                lang=self.__lang_code
            )
        )
        self.media_screen_number_backglass_label.config(
            text=Context.get_text(
                'setup_screen_number',
                lang=self.__lang_code
            )
        )

        self.media_full_dmd_label.config(
            text=Context.get_text(
                Media.FULL_DMD.value,
                lang=self.__lang_code
            )
        )
        self.media_screen_number_full_dmd_label.config(
            text=Context.get_text(
                'setup_screen_number',
                lang=self.__lang_code
            )
        )

        self.media_playfield_label.config(
            text=Context.get_text(
                Media.PLAYFIELD.value,
                lang=self.__lang_code
            )
        )
        self.media_screen_number_playfield_label.config(
            text=Context.get_text(
                'setup_screen_number',
                lang=self.__lang_code
            )
        )

        self.media_audio_label.config(
            text=Context.get_text(
                Media.AUDIO.value,
                lang=self.__lang_code
            )
        )

        self.media_dmd_label.config(
            text=Context.get_text(
                Media.DMD.value,
                lang=self.__lang_code
            )
        )

        self.media_flyer_label.config(
            text=Context.get_text(
                Media.FLYER.value,
                lang=self.__lang_code
            )
        )

        self.media_help_label.config(
            text=Context.get_text(
                Media.HELP.value,
                lang=self.__lang_code
            )
        )

        self.media_other_label.config(
            text=Context.get_text(
                Media.OTHER.value,
                lang=self.__lang_code
            )
        )

        self.media_wheel_bar_label.config(
            text=Context.get_text(
                Media.WHEEL_BAR.value,
                lang=self.__lang_code
            )
        )

        self.media_wheel_image_label.config(
            text=Context.get_text(
                Media.WHEEL_IMAGE.value,
                lang=self.__lang_code
            )
        )

        self.button_cancel.config(
            text=Context.get_text(
                'cancel',
                lang=self.__lang_code
            )
        )

        self.button_validate.config(
            text=Context.get_text(
                'validate',
                lang=self.__lang_code
            )
        )
