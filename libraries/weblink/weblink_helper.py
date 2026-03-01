#!/usr/bin/python3
"""Weblink Helper"""

import webbrowser


class WeblinkHelper:
    """Class to help usage of Weblink"""

    @staticmethod
    def is_weblink(
        url_text: str
    ):
        """Check if the url_text is a Weblink"""
        return url_text.startswith(("http://", "https://"))

    @staticmethod
    def open_weblink(
        url_text: str
    ) -> bool:
        """Open a Weblink"""

        if not WeblinkHelper.is_weblink(
            url_text=url_text
        ):
            return False

        return webbrowser.open(url_text)
