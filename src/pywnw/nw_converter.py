"""Provide an novelWriter converter class for yWriter.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os

from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywriter.yw.yw7_file import Yw7File
from pywnw.nw_project import NwProject


class NwConverter(YwCnvUi):
    """A converter class for yWriter and novelWriter."""

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.
        Override the superclass method.
        """
        self.newFile = None

        if not os.path.isfile(sourcePath):
            self.ui.set_info_how('ERROR: File "' + os.path.normpath(sourcePath) + '" not found.')
            return

        fileName, fileExtension = os.path.splitext(sourcePath)

        if fileExtension == Yw7File.EXTENSION:
            sourceFile = Yw7File(sourcePath, **kwargs)
            targetFile = NwProject(fileName + NwProject.EXTENSION, **kwargs)
            targetFile.ywProject = sourceFile
            self.export_from_yw(sourceFile, targetFile)

        elif fileExtension == NwProject.EXTENSION:
            sourceFile = NwProject(sourcePath, **kwargs)
            targetFile = Yw7File(fileName + Yw7File.EXTENSION, **kwargs)

            if os.path.isfile(fileName + Yw7File.EXTENSION):
                sourceFile.ywProject = targetFile
                self.import_to_yw(sourceFile, targetFile)

            else:
                self.create_yw7(sourceFile, targetFile)

        else:
            self.ui.set_info_how('ERROR: File type of "' + os.path.normpath(sourcePath) + '" not supported.')
