"""Provide an novelWriter converter class for yWriter.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os

from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywriter.ui.ui import Ui
from pywriter.yw.yw7_file import Yw7File
from pywnw.nwx_file import NwxFile


class NwConverter(YwCnvUi):
    """A converter class for yWriter and novelWriter."""

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.
        Override the superclass method.
        """

        if not os.path.isfile(sourcePath):
            self.ui.set_info_how('ERROR: File "{}" not found.'.format(os.path.normpath(sourcePath)))
            return

        fileName, fileExtension = os.path.splitext(sourcePath.replace('\\', '/'))
        srcDir = os.path.dirname(sourcePath).replace('\\', '/')

        if srcDir == '':
            srcDir = '.'

        srcDir += '/'

        if fileExtension == Yw7File.EXTENSION:
            sourceFile = Yw7File(sourcePath, **kwargs)
            title = fileName.replace(srcDir, '')
            prjDir = srcDir + title + '.nw'

            if os.path.isfile('{}/nwProject.lock'.format(prjDir)):
                self.ui.set_info_how('ERROR: Please exit novelWriter.')
                return

            try:
                os.makedirs(prjDir + NwxFile.CONTENT_DIR)

            except FileExistsError:
                extension = '.bak'
                i = 0

                while os.path.isdir(prjDir + extension):
                    extension = '.bk{:03d}'.format(i)
                    i += 1

                    if i > 999:
                        self.ui.set_info_how('ERROR: Unable to back up the project.')
                        return

                os.replace(prjDir, prjDir + extension)
                self.ui.set_info_what('Backup folder "{}{}" saved.'.format(os.path.normpath(prjDir), extension))
                os.makedirs(prjDir + NwxFile.CONTENT_DIR)

            targetFile = NwxFile('{}/nwProject.nwx'.format(prjDir), **kwargs)
            self.export_from_yw(sourceFile, targetFile)

        elif fileExtension == NwxFile.EXTENSION:
            sourceFile = NwxFile(sourcePath, **kwargs)

            prjDir = '{}/../'.format(srcDir)
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

            if os.path.isfile(fileName):

                if self.confirm_overwrite(fileName):
                    os.replace(fileName, '{}.bak'.format(fileName))
                    self.ui.set_info_what('Backup file "{}.bak" saved.'.format(os.path.normpath(sourcePath)))

                else:
                    self.ui.set_info_what('Action canceled by user.')
                    return

            targetFile = Yw7File(fileName, **kwargs)
            self.create_yw7(sourceFile, targetFile)

        else:
            self.ui.set_info_how('ERROR: File type of "{}" not supported.'.format(os.path.normpath(sourcePath)))
