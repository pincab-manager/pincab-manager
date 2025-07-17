#!/usr/bin/python3
"""XML Helper"""

import os
from libraries.context.context import Context
from libraries.file.file_helper import FileHelper
from libraries.logging.logging_helper import LoggingHelper


class XmlHelper:
    """Class to help usage of XML"""

    @staticmethod
    def is_tag(
        xml_file_path: str,
        tag: str
    ):
        """Specify if tag in XML file"""

        # Load XML files
        xml_content = FileHelper.read_file(
            file_path=xml_file_path
        )
        for line in xml_content.splitlines():
            if line.strip() == f'<{tag}>':
                return True

        return False

    @staticmethod
    def extract_tags(
        xml_file_path: str,
        extracted_file_path: str,
        tags: list
    ):
        """Extract tags in a XML file from a XML file"""

        # Load XML file
        xml_content = FileHelper.read_file(
            file_path=xml_file_path
        )
        export_content = ''
        for tag in tags:
            tag_line = False
            for line in xml_content.splitlines():
                if line.strip() == f'<{tag}>':
                    tag_line = True
                if tag_line:
                    if len(export_content) > 0:
                        export_content += '\n'
                    export_content += line
                if line.strip() == f'</{tag}>':
                    tag_line = False

        if len(export_content) == 0:
            return

        if Context.is_simulated():
            LoggingHelper.log_info(
                message=Context.get_text(
                    'extract_tags_simulation',
                    file=str(extracted_file_path)
                )
            )
            return

        LoggingHelper.log_info(
            message=Context.get_text(
                'extract_tags_in_progress',
                file=str(extracted_file_path)
            )
        )
        os.makedirs(os.path.dirname(extracted_file_path), exist_ok=True)
        FileHelper.write_file(
            file_path=extracted_file_path,
            content=export_content
        )

    @staticmethod
    def delete_tags(
        xml_file_path: str,
        tags: list
    ):
        """Delete tags from XML file"""

        # Load XML files
        xml_content = FileHelper.read_file(
            file_path=xml_file_path
        )
        new_content = ''
        tag_line = False
        for line in xml_content.splitlines():
            for tag in tags:
                if line.strip() == f'<{tag}>':
                    tag_line = True
            if not tag_line:
                new_content += line + '\n'
            for tag in tags:
                if line.strip() == f'</{tag}>':
                    tag_line = False

        FileHelper.write_file(
            file_path=xml_file_path,
            content=new_content
        )

    @staticmethod
    def import_tags(
        xml_file_path: str,
        extracted_file_path: str,
        parent_tag: str
    ):
        """Import tags in a XML file from a XML file"""

        # Load XML files
        xml_content = FileHelper.read_file(
            file_path=xml_file_path
        )
        tags_content = FileHelper.read_file(
            file_path=extracted_file_path
        )
        new_content = ''
        for line in xml_content.splitlines():
            if line.strip() == f'</{parent_tag}>':
                new_content += tags_content + '\n'
            new_content += line + '\n'

        FileHelper.write_file(
            file_path=xml_file_path,
            content=new_content
        )
