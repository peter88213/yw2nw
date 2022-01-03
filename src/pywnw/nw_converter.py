"""Provide an novelWriter converter class for yWriter.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywriter.yw.yw7_file import Yw7File
from pywnw.nw_project import NwProject


class NwConverter(YwCnvUi):
    """A converter class for NovelWriter."
    Extend the Super class. 
    Show 'Open' button after conversion from yw.
    """
    EXPORT_SOURCE_CLASSES = [Yw7File]
    EXPORT_TARGET_CLASSES = [NwProject]

    def export_from_yw(self, sourceFile, targetFile):
        """Extend the super class method, showing an 'open' button after conversion."""
        YwCnvUi.export_from_yw(self, sourceFile, targetFile)

        try:
            if self.newFile:
                self.ui.show_open_button(self.open_newFile)

        except AttributeError:
            pass
