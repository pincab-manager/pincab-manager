#!/usr/bin/python3
"""UI Media"""

import os
import re
import threading
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog
from typing import List, Optional

import vlc

from dialogs.waiting.waiting_dialog import WaitingDialog
from libraries.cmd.cmd_helper import CmdHelper
from libraries.context.context import Context
from libraries.constants.constants import Constants
from libraries.file.file_helper import FileHelper
from libraries.logging.logging_helper import LoggingHelper

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-nested-blocks
# pylint: disable=attribute-defined-outside-init


class UIMediaModeConfig:
    """Structure to define a media mode's config"""

    def __init__(
        self,
        mode: str,
        folder: str,
        name_suffix: Optional[str] = None
    ):
        """Initialize structure"""

        self.mode = mode
        self.folder = folder
        self.name_suffix = name_suffix


class UIMedia(tk.LabelFrame):
    """Class for UI Media"""

    _YOUTUBE_REGEX = r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/[^&]+$"

    def __init__(
        self,
        update_media_actions,
        parent: any,
        title: str,
        modes_configs: List[UIMediaModeConfig],
        width: int,
        height: int,
        rotate=0
    ):
        """Initialize UI"""

        super().__init__(
            parent,
            text=title
        )

        self.__title = title
        self.__update_media_actions = update_media_actions
        self.__analysis_enabled = False
        self.__vlc_window = None
        self.__vlc_media_player = None
        self.__item_id = None
        self.__media_path = None
        self.__mode = None
        self.__muted = False
        self.__current_media_audio = False
        self.__current_audio_analysis = False
        self.__current_video_analysis = False
        self.__current_media_video = False
        self.__current_media_photo = False
        self.__current_parent_path = None
        self.__current_file_name = None
        self.__current_file_path = None
        self.__transform_options = None
        self.__transform_extension = None
        self.__transform_destination_file_path = None

        # Store the modes configs
        self.__modes_configs = modes_configs

        # Create frame for icons
        icons_frame = tk.Frame(self)
        icons_frame.pack(
            side=tk.LEFT,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )

        # Create icons
        self.__audio_icon_label = tk.Label(icons_frame)
        self.__audio_icon_label.pack(
            side=tk.TOP,
            pady=Constants.UI_PAD_SMALL
        )
        self.__photo_video_icon_label = tk.Label(icons_frame)
        self.__photo_video_icon_label.pack(
            side=tk.TOP,
            pady=Constants.UI_PAD_SMALL
        )

        # Create frame to show media
        self.__media_frame = tk.Frame(self)
        self.__media_frame.pack(
            side=tk.TOP,
            padx=Constants.UI_PAD_SMALL,
            pady=Constants.UI_PAD_SMALL
        )
        self.__media_frame.config(width=width, height=height)

        # Initialize VLC
        self.__init_vlc_params = []
        if rotate != 0:
            self.__init_vlc_params = [
                '--video-filter=transform',
                f'--transform-type={rotate}'
            ]
        self.__vlc_instance = vlc.Instance(*self.__init_vlc_params)

        # Build a media's player
        self.__media_player = self.__vlc_instance.media_player_new()

        # Define where the media will be played
        self.__media_frame.update_idletasks()
        self.__media_player.set_hwnd(self.__media_frame.winfo_id())

        # Bind clicks
        self.bind("<Button-3>", self.__show_context_menu)
        self.__audio_icon_label.bind("<Button-3>", self.__show_context_menu)
        self.__photo_video_icon_label.bind(
            "<Button-3>", self.__show_context_menu)
        self.__media_frame.bind("<Button-3>", self.__show_context_menu)

    def __show_context_menu(self, event):
        """Show context menu"""

        # Build context menu
        context_menu = tk.Menu(self, tearoff=0)

        # Actions to open/explore media
        if self.__current_file_path is not None:
            context_menu.add_command(
                label=Context.get_text('media_action_open_vlc'),
                command=self.__open_vlc_window
            )

        context_menu.add_command(
            label=Context.get_text(
                'target_action_explore',
                target=Context.get_text('target_folder')
            ),
            command=self.__explore_folder
        )
        context_menu.add_separator()

        # Actions to export/import/delete media
        context_menu.add_command(
            label=Context.get_text(
                'target_action_import',
                target=Context.get_text('target_media')
            ),
            command=self.__import_media
        )

        if self.__current_file_path is not None:
            context_menu.add_command(
                label=Context.get_text(
                    'target_action_export',
                    target=Context.get_text('target_media')
                ),
                command=self.__export_media
            )

        if self.__current_file_path is not None:
            context_menu.add_command(
                label=Context.get_text(
                    'target_action_delete',
                    target=Context.get_text('target_media')
                ),
                command=self.__delete_media
            )

        context_menu.add_separator()

        # Actions for YouTube
        context_menu.add_command(
            label=Context.get_text(
                'target_action_import',
                target=Context.get_text('target_video_youtube')
            ),
            command=self.__import_youtube
        )
        context_menu.add_command(
            label=Context.get_text(
                'target_action_download',
                target=Context.get_text('target_video_youtube')
            ),
            command=self.__download_youtube
        )
        context_menu.add_separator()

        # Actions for video/photo
        if self.__current_media_audio and self.__current_media_video:
            context_menu.add_command(
                label=Context.get_text('media_action_extract_video'),
                command=self.__extract_video
            )
        if self.__current_media_video or self.__current_media_photo:
            context_menu.add_command(
                label=Context.get_text('media_action_horizontal_flip'),
                command=self.__horizontal_flip_media
            )
            context_menu.add_command(
                label=Context.get_text('media_action_vertical_flip'),
                command=self.__vertical_flip_media
            )
            context_menu.add_command(
                label=Context.get_text('media_action_rotate'),
                command=self.__rotate_media
            )

        if self.__current_media_audio and self.__current_media_video:
            context_menu.add_command(
                label=Context.get_text('media_action_remove_video'),
                command=self.__remove_video
            )

        if self.__current_media_video or self.__current_media_photo:
            context_menu.add_separator()

        # Actions for audio
        if self.__current_media_audio and self.__current_media_video:
            context_menu.add_command(
                label=Context.get_text('media_action_extract_audio'),
                command=self.__extract_audio
            )

        if self.__current_media_audio:
            context_menu.add_command(
                label=Context.get_text('media_action_increase_volume'),
                command=self.__increase_volume
            )
            context_menu.add_command(
                label=Context.get_text('media_action_decrease_volume'),
                command=self.__decrease_volume
            )

        if self.__current_media_audio and self.__current_media_video:
            context_menu.add_command(
                label=Context.get_text('media_action_remove_audio'),
                command=self.__remove_audio
            )

        if self.__current_media_audio:
            context_menu.add_separator()

        # Actions to mute/unmute
        if not self.__muted:
            context_menu.add_command(
                label=Context.get_text('media_action_mute'),
                command=self.toggle_mute_unmute
            )
        else:
            context_menu.add_command(
                label=Context.get_text('media_action_unmute'),
                command=self.toggle_mute_unmute
            )

        # Show context menu in the mouse's position
        context_menu.post(event.x_root, event.y_root)

        # Don't execute any other action in the button
        return "break"

    def __open_vlc_window(self):
        """Open the current media in a VLC window"""

        # Close VLC window if already open
        self.__close_vlc_window()

        # Create a new tkinter window
        self.__vlc_window = tk.Toplevel(self)
        self.__vlc_window.title(Context.get_text('media_title'))
        self.__vlc_window.geometry("800x600")

        # Initialize a new media player for the window
        self.__vlc_media_player = self.__vlc_instance.media_player_new()

        # Attach the video to the handle of the new window
        self.__vlc_window.update_idletasks()
        self.__vlc_media_player.set_hwnd(self.__vlc_window.winfo_id())

        # Set the media currently playing
        current_media = self.__media_player.get_media()
        if current_media:
            self.__vlc_media_player.set_media(current_media)

            # Play the video in the new window
            self.__vlc_media_player.play()

        # Add an action to exit fullscreen mode
        self.__vlc_window.bind(
            '<Escape>', lambda event: self.__close_vlc_window()
        )

        # Handle the window's close button (top-right 'X')
        self.__vlc_window.protocol("WM_DELETE_WINDOW", self.__close_vlc_window)

        # Set focus to the new window
        self.__vlc_window.focus_set()  # Set focus to the new window

        # Bring the window to the top of the stack
        self.__vlc_window.lift()

    def __explore_folder(self):
        """Explore the current folder in Windows Explorer"""

        FileHelper.explore_folder(
            folder_path=self.__current_parent_path
        )

    def __close_vlc_window(self):
        """Close VLC window"""

        if self.__vlc_window is not None:
            self.__vlc_media_player.stop()
            self.__vlc_window.destroy()
            self.__vlc_window = None

    def __import_media(self):
        """Import media from a file"""

        self.__source_file_path = filedialog.askopenfilename(
            parent=self.winfo_toplevel()
        )
        if self.__source_file_path:
            # Retrieve extension
            _, file_extension = os.path.splitext(self.__source_file_path)

            # Do nothing if the file is not a media file
            if file_extension not in Constants.VLC_SUPPORTED_EXTENSIONS:
                messagebox.showwarning(
                    Context.get_text('warning'),
                    Context.get_text('warning_not_a_media_file'),
                    parent=self.winfo_toplevel()
                )
                return

            # Execute the import in a waiting dialog
            WaitingDialog(
                parent=self.winfo_toplevel(),
                process_name=Context.get_text('process_importation'),
                process_function=self.__run_import_media
            )

    def __run_import_media(self, should_interrupt):
        """Run import media from a file"""

        # pylint: disable=unused-argument

        # Retrieve extension
        _, file_extension = os.path.splitext(self.__source_file_path)

        # Delete current file path is exists
        if self.__current_file_path is not None:
            # Close VLC window if already open
            self.__close_vlc_window()

            # Stop the media
            self.__media_player.stop()

            # Delete the current file
            FileHelper.delete_file(
                file_path=self.__current_file_path
            )

        # Copy new media file
        FileHelper.copy_file(
            source_file_path=self.__source_file_path,
            destination_file_path=os.path.join(
                self.__current_parent_path,
                self.__current_file_name + file_extension
            )
        )

        # Play new media file
        self.update_media(
            item_id=self.__item_id,
            media_path=self.__media_path,
            mode=self.__mode,
            analysis_enabled=self.__analysis_enabled
        )

        # Advise that media's status changed
        self.__update_media_actions()

    def __export_media(self):
        """Export media in a file"""

        if self.__current_file_path is None:
            return

        # Retrieve extension
        _, file_extension = os.path.splitext(self.__current_file_path)

        # Retrieve initial file name
        initial_file_name = self.__title.replace('/', '_')
        initial_file_name += '_'
        initial_file_name += self.__current_file_name
        initial_file_name += file_extension

        # Ask destination file's path
        self.__destination_file_path = filedialog.asksaveasfilename(
            parent=self.winfo_toplevel(),
            initialfile=initial_file_name,
            defaultextension=file_extension,
            filetypes=[
                (Context.get_text('media_type'), f'*{file_extension}')
            ]
        )
        if self.__destination_file_path:
            # Execute the import in a waiting dialog
            WaitingDialog(
                parent=self.winfo_toplevel(),
                process_name=Context.get_text('process_exportation'),
                process_function=self.__run_export_media
            )

    def __run_export_media(self, should_interrupt):
        """Run export media"""

        # pylint: disable=unused-argument

        FileHelper.copy_file(
            source_file_path=self.__current_file_path,
            destination_file_path=self.__destination_file_path
        )

    def __run_youtube(self, should_interrupt):
        """Run import/download from YouTube"""

        # Stop current media if import
        if self.__action == 'import':
            # Close VLC window if already open
            self.__close_vlc_window()

            # Stop the media
            self.__media_player.stop()

        # Create dirs if missing
        os.makedirs(self.__destination_path, exist_ok=True)

        # Execute yt-dlp
        final_video_output_path = os.path.join(
            self.__destination_path,
            'output.mp4'
        )
        final_audio_output_path = os.path.join(
            self.__destination_path,
            'output.m4a'
        )
        command = 'start cmd /c'
        command += ' "'
        command += f'cd /d "{self.__destination_path}" && '
        command += str(Context.get_yt_dlp_path())
        command += ' -f "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]"'
        # Merge using ffmpeg if no separation audio/video
        if not self.__separate_audio_video:
            command += ' --ffmpeg-location "'
            command += str(Context.get_ffmpeg_path())
            command += '"'
            command += ' --postprocessor-args "ffmpeg:-t 00:30:00 -c:v libx264 -crf 23"'
            command += ' --merge-output-format mp4'
        command += f' -o "temporary.mp4" "{self.youtube_link}"'
        command += ' && cmd /c "for %f in (temporary*.mp4 temporary*.m4a) do ren "%f" output%~xf"'
        command += ' "'
        CmdHelper.run(
            command,
            check=False
        )

        # Wait for end processing
        while not Context.is_simulated() and not os.path.exists(final_video_output_path):

            if should_interrupt():
                return

            # Sleep 0.1 seconde
            time.sleep(0.1)

        # If import, delete the existing Media
        if self.__action == 'import' and self.__current_file_path is not None:
            FileHelper.delete_file(
                file_path=self.__current_file_path
            )

        # Move output to destination file
        FileHelper.copy_file(
            source_file_path=final_video_output_path,
            destination_file_path=os.path.join(
                self.__destination_path,
                self.__current_file_name + '.mp4'
            )
        )
        FileHelper.delete_file(
            file_path=final_video_output_path
        )
        if self.__separate_audio_video:
            FileHelper.copy_file(
                source_file_path=final_audio_output_path,
                destination_file_path=os.path.join(
                    self.__destination_path,
                    self.__current_file_name + '.m4a'
                )
            )
            FileHelper.delete_file(
                file_path=final_audio_output_path
            )

        # If import, play new media file if possible
        if self.__action == 'import':
            self.update_media(
                item_id=self.__item_id,
                media_path=self.__media_path,
                mode=self.__mode,
                analysis_enabled=self.__analysis_enabled
            )

            # Advise that media's status changed
            self.__update_media_actions()

    def __download_youtube(self):
        """Download a media from YouTube"""
        self.__action = 'download'

        # Ask an entry for the YouTube's link
        while True:
            self.youtube_link = simpledialog.askstring(
                Context.get_text('confirmation'),
                Context.get_text('confirm_youtube'),
                parent=self.winfo_toplevel()
            )
            if self.youtube_link is None:
                break
            if re.fullmatch(UIMedia._YOUTUBE_REGEX, self.youtube_link):
                break

        if self.youtube_link is None:
            return

        # Ask if merge audio/video has to be done
        self.__separate_audio_video = messagebox.askyesno(
            Context.get_text('question'),
            Context.get_text('question_separate_audio_video'),
            parent=self.winfo_toplevel()
        )

        # Ask destination path
        self.__destination_path = filedialog.askdirectory(
            parent=self.winfo_toplevel()
        )
        if self.__destination_path:
            # Execute the process in a waiting dialog
            WaitingDialog(
                parent=self.winfo_toplevel(),
                process_name=Context.get_text('process_download'),
                process_function=self.__run_youtube
            )

    def __import_youtube(self):
        """Import a media from YouTube"""
        self.__action = 'import'

        # Ask an entry for the YouTube's link
        while True:
            self.youtube_link = simpledialog.askstring(
                Context.get_text('confirmation'),
                Context.get_text('confirm_youtube'),
                parent=self.winfo_toplevel()
            )
            if self.youtube_link is None:
                break
            if re.fullmatch(UIMedia._YOUTUBE_REGEX, self.youtube_link):
                break

        if self.youtube_link is None:
            return

        # Destinatioon path is the current parent path
        self.__destination_path = self.__current_parent_path

        # No separation for audio/video
        self.__separate_audio_video = False

        # Execute the process in a waiting dialog
        WaitingDialog(
            parent=self.winfo_toplevel(),
            process_name=Context.get_text('process_importation'),
            process_function=self.__run_youtube
        )

    def __extract_video(self):
        """Extract video"""

        if self.__current_file_path is None:
            return

        # Retrieve extension
        _, file_extension = os.path.splitext(self.__current_file_path)

        # Retrieve initial file name
        initial_file_name = self.__title.replace('/', '_')
        initial_file_name += '_'
        initial_file_name += self.__current_file_name
        initial_file_name += file_extension

        # Ask destination file's path
        destination_file_path = filedialog.asksaveasfilename(
            parent=self.winfo_toplevel(),
            initialfile=initial_file_name,
            defaultextension=file_extension,
            filetypes=[
                (Context.get_text('media_type'), f'*{file_extension}')
            ]
        )
        if destination_file_path:
            self.__transform_media(
                transform_options='-an -c:v libx264 -crf 23 -preset veryfast',
                transform_destination_file_path=destination_file_path
            )

    def __extract_audio(self):
        """Extract audio"""

        if self.__current_file_path is None:
            return

        # Retrieve extension
        extension = '.mp3'

        # Retrieve initial file name
        initial_file_name = self.__title
        initial_file_name += '_'
        initial_file_name += self.__current_file_name
        initial_file_name += extension

        # Ask destination file's path
        destination_file_path = filedialog.asksaveasfilename(
            parent=self.winfo_toplevel(),
            initialfile=initial_file_name,
            defaultextension=extension,
            filetypes=[
                (Context.get_text('media_audio'), f'*{extension}')
            ]
        )
        if destination_file_path:
            self.__transform_media(
                transform_options='-vn -acodec libmp3lame -q:a 2',
                transform_extension=extension,
                transform_destination_file_path=destination_file_path
            )

    def __delete_media(self):
        """Delete media"""

        if self.__current_file_path is None:
            return

        if messagebox.askokcancel(
            Context.get_text('confirmation'),
            Context.get_text('confirm_delete_media'),
            parent=self.winfo_toplevel()
        ):

            # Execute the delete in a waiting dialog
            WaitingDialog(
                parent=self.winfo_toplevel(),
                process_name=Context.get_text('process_deletion'),
                process_function=self.__run_delete_media
            )

    def __run_delete_media(self, should_interrupt):
        """Run delete media"""

        # pylint: disable=unused-argument

        # Close VLC window if already open
        self.__close_vlc_window()

        # Stop the media
        self.__media_player.stop()

        # Delete the current file
        FileHelper.delete_file(
            file_path=self.__current_file_path
        )

        # Play new media file if possible
        self.update_media(
            item_id=self.__item_id,
            media_path=self.__media_path,
            mode=self.__mode,
            analysis_enabled=self.__analysis_enabled
        )

        # Advise that media's status changed
        self.__update_media_actions()

    def __run_analysis(self, file_path, media):
        """Run analysis for the specified media"""

        try:
            # Wait for the media to be ready
            state = self.__media_player.get_state()
            while state not in [
                vlc.State.Playing,
                vlc.State.Ended,
                vlc.State.Error
            ]:
                state = self.__media_player.get_state()

            # Identify if audio/video/photo in the media
            if self.__current_file_path.endswith('.ogg'):
                self.__current_media_audio = True
            media.parse_with_options(1, timeout=5000)
            if media.get_duration() == 10000:
                self.__current_media_photo = True
            else:
                tracks = media.tracks_get()
                if tracks is not None:
                    for track in tracks:
                        if track.type == vlc.TrackType.video:
                            self.__current_media_video = True

                            # Specify end of current video analysis
                            self.__current_video_analysis = False

                            # Update icons
                            self.__update_icons()
                        if not self.__current_media_audio and \
                                not self.__muted and \
                                track.type == vlc.TrackType.audio:

                            # Execute ffmpeg in a subprocess
                            command = str(Context.get_ffmpeg_path())
                            command += f' -i "{file_path}" '
                            command += '-af volumedetect -f null /dev/null'
                            ffmpeg_result = CmdHelper.retrieve_cmd_result(
                                read_cmd=command
                            )

                            # Check if max volume is upper than -50
                            max_volume = -50
                            for line in ffmpeg_result.stderr.splitlines():
                                if "max_volume" in line:
                                    max_volume = float(
                                        line.split(':')[
                                            1].strip().split(' ')[0]
                                    )
                                    break

                            # Check if current file didn't change
                            if self.__current_file_path != file_path:
                                return

                            # Update indicator for media audio
                            self.__current_media_audio = max_volume > -50

                            # Specify end of current audio analysis
                            self.__current_audio_analysis = False

                            # Update icons
                            self.__update_icons()

            # Specify end of current analysis
            self.__current_audio_analysis = False
            self.__current_video_analysis = False

            # Update icons
            self.__update_icons()

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
                parent=self.winfo_toplevel()
            )

    def __run_transformation(self, should_interrupt):
        """Run transformation"""

        # Close VLC window if already open
        self.__close_vlc_window()

        # Stop the media
        self.__media_player.stop()

        # Retrieve extension
        _, file_extension = os.path.splitext(
            self.__current_file_path
        )

        extension = file_extension
        if self.__transform_extension is not None:
            extension = self.__transform_extension

        # Execute ffmpeg
        temporary_output_path = os.path.join(
            self.__current_parent_path,
            'temporary' + extension
        )
        final_output_file_name = 'output' + extension
        final_output_path = os.path.join(
            self.__current_parent_path,
            final_output_file_name
        )
        command = 'start cmd /c'
        command += ' "'
        command += str(Context.get_ffmpeg_path())
        command += f' -i "{self.__current_file_path}"'
        command += f' {self.__transform_options}'
        command += f' "{temporary_output_path}"'
        command += ' && ren'
        command += f' "{temporary_output_path}" "{final_output_file_name}"'
        command += ' "'
        CmdHelper.run(
            command,
            check=False
        )

        # Wait for end processing
        while not Context.is_simulated() and not os.path.exists(final_output_path):

            if should_interrupt():
                return

            # Sleep 0.1 seconde
            time.sleep(0.1)

        if self.__transform_destination_file_path is not None:
            # Move the output file in the destination
            FileHelper.copy_file(
                source_file_path=final_output_path,
                destination_file_path=self.__transform_destination_file_path
            )
            FileHelper.delete_file(
                file_path=final_output_path
            )
        else:
            # If new extension
            if self.__transform_extension is not None:
                FileHelper.delete_file(
                    file_path=self.__current_file_path
                )
                self.__current_file_path = self.__current_file_path.replace(
                    file_extension,
                    extension
                )
                self.__current_file_name = self.__current_file_name.replace(
                    file_extension,
                    extension
                )

            # Override the existing file by the output file
            FileHelper.copy_file(
                source_file_path=final_output_path,
                destination_file_path=self.__current_file_path
            )
            FileHelper.delete_file(
                file_path=final_output_path
            )

        # Play new media file if possible
        self.update_media(
            item_id=self.__item_id,
            media_path=self.__media_path,
            mode=self.__mode,
            analysis_enabled=self.__analysis_enabled
        )

        # Advise that media's status changed
        self.__update_media_actions()

    def __transform_media(
        self,
        transform_options: str,
        transform_extension=None,
        transform_destination_file_path=None
    ):
        """Transform the current media"""

        if self.__current_file_path is None:
            return

        self.__transform_options = transform_options
        self.__transform_extension = transform_extension
        self.__transform_destination_file_path = transform_destination_file_path

        # Execute the process in a waiting dialog
        WaitingDialog(
            parent=self.winfo_toplevel(),
            process_name=Context.get_text('process_transformation'),
            process_function=self.__run_transformation
        )

    def __rotate_media(self):
        """Rotate the current media"""

        if self.__current_file_path is None:
            return

        if messagebox.askokcancel(
            Context.get_text('confirmation'),
            Context.get_text('confirm_rotate_media'),
            parent=self.winfo_toplevel()
        ):
            if self.__current_media_photo:
                self.__transform_media(
                    transform_options='-vf "transpose=1"'
                )
            else:
                self.__transform_media(
                    transform_options='-vf "transpose=1" -c:v libx264 -crf 23 -preset veryfast'
                )

    def __horizontal_flip_media(self):
        """Horizontal flip the current media"""

        if self.__current_file_path is None:
            return

        if messagebox.askokcancel(
            Context.get_text('confirmation'),
            Context.get_text('confirm_horizontal_flip_media'),
            parent=self.winfo_toplevel()
        ):
            if self.__current_media_photo:
                self.__transform_media(
                    transform_options='-vf "hflip"'
                )
            else:
                self.__transform_media(
                    transform_options='-vf "hflip" -c:v libx264 -crf 23 -preset veryfast'
                )

    def __vertical_flip_media(self):
        """Vertical flip the current media"""

        if self.__current_file_path is None:
            return

        if messagebox.askokcancel(
            Context.get_text('confirmation'),
            Context.get_text('confirm_vertical_flip_media'),
            parent=self.winfo_toplevel()
        ):
            if self.__current_media_photo:
                self.__transform_media(
                    transform_options='-vf "vflip"'
                )
            else:
                self.__transform_media(
                    transform_options='-vf "vflip" -c:v libx264 -crf 23 -preset veryfast'
                )

    def __increase_volume(self):
        """Increase volume in the current media"""

        if self.__current_file_path is None:
            return

        # Ask an entry for the new version
        while True:
            volume = simpledialog.askstring(
                Context.get_text('confirmation'),
                Context.get_text(
                    'confirm_increase_volume'
                ),
                parent=self.winfo_toplevel()
            )
            if volume is None:
                return
            try:
                if float(volume) > 1:
                    break
            except ValueError:
                continue

        if self.__current_media_video:
            self.__transform_media(
                transform_options=f'-c:v copy -af "volume={volume}"'
            )
        else:
            self.__transform_media(
                transform_options=f'-af "volume={volume}"'
            )

    def __decrease_volume(self):
        """decrease volume in the current media"""

        if self.__current_file_path is None:
            return

        # Ask an entry for the new version
        while True:
            volume = simpledialog.askstring(
                Context.get_text('confirmation'),
                Context.get_text(
                    'confirm_decrease_volume'
                ),
                parent=self.winfo_toplevel()
            )
            if volume is None:
                return
            try:
                if 0 < float(volume) < 1:
                    break
            except ValueError:
                continue

        if self.__current_media_video:
            self.__transform_media(
                transform_options=f'-c:v copy -af "volume={volume}"'
            )
        else:
            self.__transform_media(
                transform_options=f'-af "volume={volume}"'
            )

    def __remove_audio(self):
        """Remove audio in the current media"""

        if self.__current_file_path is None:
            return

        if messagebox.askokcancel(
            Context.get_text('confirmation'),
            Context.get_text('confirm_remove_audio'),
            parent=self.winfo_toplevel()
        ):
            self.__transform_media(
                transform_options='-an -c:v libx264 -crf 23 -preset veryfast'
            )

    def __remove_video(self):
        """Remove video in the current media"""

        if self.__current_file_path is None:
            return

        if messagebox.askokcancel(
            Context.get_text('confirmation'),
            Context.get_text('confirm_remove_video'),
            parent=self.winfo_toplevel()
        ):
            self.__transform_media(
                transform_options='-vn -acodec libmp3lame -q:a 2',
                transform_extension='.mp3'
            )

    def __update_icons(self):
        """Update icons"""

        # Update Audio icon
        audio_icon_file_name = None
        if self.__muted:
            audio_icon_file_name = 'audio_mute.png'
        elif self.__current_audio_analysis:
            audio_icon_file_name = 'in_progress.png'
        elif self.__current_media_audio:
            audio_icon_file_name = 'audio_on.png'
        else:
            audio_icon_file_name = 'audio_off.png'
        audio_icon_path = os.path.join(
            Context.get_base_path(),
            Constants.RESOURCES_PATH,
            'img',
            audio_icon_file_name
        )
        audio_icon_img = tk.PhotoImage(
            file=audio_icon_path
        )
        self.__audio_icon_label.configure(
            image=audio_icon_img
        )
        if self.__analysis_enabled:
            self.__audio_icon_label.image = audio_icon_img

        # Update Photo/Video icon
        photo_video_icon_file_name = None
        if self.__current_video_analysis:
            photo_video_icon_file_name = 'in_progress.png'
        elif self.__current_media_photo:
            photo_video_icon_file_name = 'photo_on.png'
        elif self.__current_media_video:
            photo_video_icon_file_name = 'video_on.png'
        else:
            photo_video_icon_file_name = 'video_off.png'
        photo_video_icon_path = os.path.join(
            Context.get_base_path(),
            Constants.RESOURCES_PATH,
            'img',
            photo_video_icon_file_name
        )
        video_icon_img = tk.PhotoImage(
            file=photo_video_icon_path
        )
        self.__photo_video_icon_label.configure(
            image=video_icon_img
        )
        if self.__analysis_enabled:
            self.__photo_video_icon_label.image = video_icon_img

    def is_muted(self):
        """Specify if the media is muted"""

        return self.__muted

    def toggle_mute_unmute(self):
        """Mute or unmute the media"""

        # Update muted status
        self.__muted = not self.__muted

        # Set VLC parameters
        vlc_params = list(self.__init_vlc_params)
        if self.__muted:
            vlc_params.append('--no-audio')

        # Stop media
        self.__media_player.stop()
        self.__vlc_instance.release()

        # Initialize VLC
        self.__vlc_instance = vlc.Instance(*vlc_params)

        # Build a media's player
        self.__media_player = self.__vlc_instance.media_player_new()

        # Define where the media will be played
        self.__media_frame.update_idletasks()
        self.__media_player.set_hwnd(self.__media_frame.winfo_id())

        # Play media file if possible
        self.update_media(
            item_id=self.__item_id,
            media_path=self.__media_path,
            mode=self.__mode,
            analysis_enabled=self.__analysis_enabled
        )

        # Advise that media's status changed
        self.__update_media_actions()

    def stop_media(self):
        """Stop the media"""

        self.__media_player.stop()
        self.__media_frame.destroy()
        self.__vlc_instance.release()

    def update_media(
        self,
        item_id: str,
        media_path: str,
        mode: str,
        analysis_enabled: bool
    ):
        """Update media"""

        self.__item_id = item_id
        self.__media_path = media_path
        self.__mode = mode
        self.__analysis_enabled = analysis_enabled
        self.__current_file_name = None
        self.__current_file_path = None
        self.__current_parent_path = None

        # Close VLC window if already open
        self.__close_vlc_window()

        # Stop the media
        self.__media_player.stop()

        # Initialize each status
        self.__current_audio_analysis = False
        self.__current_video_analysis = False
        self.__current_media_audio = False
        self.__current_media_video = False
        self.__current_media_photo = False

        # Search if a config exists for the mode specified
        for mode_config in self.__modes_configs:
            # Do nothing if bad mode
            if mode_config.mode != mode:
                continue

            # Build the current parent's path
            self.__current_parent_path = os.path.join(
                media_path,
                mode_config.folder
            )

            # Build the current file's name
            self.__current_file_name = self.__item_id
            if mode_config.name_suffix is not None:
                self.__current_file_name += mode_config.name_suffix

            # Retrieve relative paths for media
            relative_paths = FileHelper.list_relative_paths(
                folder_path=self.__current_parent_path,
                file_name=self.__current_file_name,
                error_if_not_found=False
            )

            # Do nothing if no relative path
            if len(relative_paths) == 0:
                continue

            # Show a warning if several media found
            if len(relative_paths) > 1:
                LoggingHelper.log_warning(
                    message=Context.get_text(
                        'warning_several_media_folder',
                        folder=self.__current_parent_path
                    )
                )

            for relative_path in relative_paths:
                # Do nothing if the file is not a media file
                _, file_extension = os.path.splitext(relative_path)
                if file_extension not in Constants.VLC_SUPPORTED_EXTENSIONS:
                    continue

                # Change media
                self.__current_file_path = os.path.join(
                    self.__current_parent_path,
                    relative_path
                )
                media = self.__vlc_instance.media_new(self.__current_file_path)
                self.__media_player.set_media(media)

                # Play media
                self.__media_player.play()

                if self.__analysis_enabled:
                    # Specify begin of current analysis
                    self.__current_audio_analysis = True
                    self.__current_video_analysis = True

                    # Run analysis in a thread
                    thread = threading.Thread(
                        target=self.__run_analysis,
                        args=(self.__current_file_path, media)
                    )
                    thread.start()

                break

        # Update icons
        self.__update_icons()
