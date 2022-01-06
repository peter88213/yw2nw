"""Provide an novelWriter converter class for yWriter.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import xml.etree.ElementTree as ET

from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywriter.yw.yw7_file import Yw7File
from pywnw.nw_project import NwProject


class NwConverter(YwCnvUi):
    """A converter class for yWriter and novelWriter."""

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.
        Override the superclass method.
        """

        if not os.path.isfile(sourcePath):
            self.ui.set_info_how('ERROR: File "' + os.path.normpath(sourcePath) + '" not found.')
            return

        fileName, fileExtension = os.path.splitext(sourcePath)
        srcDir = os.path.dirname(sourcePath).replace('\\', '/')

        if srcDir == '':
            srcDir = '.'

        if fileExtension == Yw7File.EXTENSION:
            sourceFile = Yw7File(sourcePath, **kwargs)
            title = fileName.replace(srcDir, '')
            prjDir = srcDir + '/' + title + '.nw'

            try:
                os.makedirs(prjDir + NwProject.CONTENT_DIR)

            except FileExistsError:
                os.replace(prjDir, prjDir + '.bak')
                os.makedirs(prjDir + NwProject.CONTENT_DIR)

            targetFile = NwProject(prjDir + '/nwProject.nwx', **kwargs)
            self.export_from_yw(sourceFile, targetFile)

        elif fileExtension == NwProject.EXTENSION:
            sourceFile = NwProject(sourcePath, **kwargs)

            prjDir = srcDir + '/../'
            message = sourceFile.read_xml_file()

            if message.startswith('ERROR'):
                return message

            root = sourceFile.tree.getroot()
            prj = root.find('project')

            if prj.find('title') is not None:
                title = prj.find('title').text

            elif prj.find('name') is not None:
                title = prj.find('name').text

            else:
                title = 'NewProject'

            fileName = prjDir + title + Yw7File.EXTENSION
            targetFile = Yw7File(fileName, **kwargs)

            if os.path.isfile(fileName):
                os.replace(fileName, fileName + '.bak')

                if self.confirm_overwrite(fileName):
                    self.create_yw7(sourceFile, targetFile)

        else:
            self.ui.set_info_how('ERROR: File type of "' + os.path.normpath(sourcePath) + '" not supported.')
