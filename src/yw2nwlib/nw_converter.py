"""Provide an novelWriter converter class for yWriter.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
from pywriter.pywriter_globals import ERROR
from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywriter.yw.yw7_file import Yw7File
from yw2nwlib.nwx_file import NwxFile


class NwConverter(YwCnvUi):
    """A converter class for yWriter and novelWriter.
    
    Public methods:
        run(sourcePath, **kwargs) -- Create source and target objects and run conversion.
    """

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.

        Positional arguments: 
            sourcePath -- str: the source file path.
        
        Required keyword arguments: 
            (see NwxFile)

        Overrides the superclass method.
        """
        if not os.path.isfile(sourcePath):
            self.ui.set_info_how(f'{ERROR}File "{os.path.normpath(sourcePath)}" not found.')
            return

        fileName, fileExtension = os.path.splitext(sourcePath.replace('\\', '/'))
        srcDir = os.path.dirname(sourcePath).replace('\\', '/')
        if not srcDir:
            srcDir = '.'
        srcDir = f'{srcDir}/'
        if fileExtension == Yw7File.EXTENSION:
            sourceFile = Yw7File(sourcePath, **kwargs)
            title = fileName.replace(srcDir, '')
            prjDir = f'{srcDir}{title}.nw'
            if os.path.isfile('{prjDir}/nwProject.lock'):
                self.ui.set_info_how(f'{ERROR}Please exit novelWriter.')
                return

            try:
                os.makedirs(prjDir + NwxFile.CONTENT_DIR)
            except FileExistsError:
                extension = '.bak'
                i = 0
                while os.path.isdir(prjDir + extension):
                    extension = f'.bk{i:03}'
                    i += 1
                    if i > 999:
                        self.ui.set_info_how(f'{ERROR}Unable to back up the project.')
                        return

                os.replace(prjDir, prjDir + extension)
                self.ui.set_info_what(f'Backup folder "{os.path.normpath(prjDir)}{extension}" saved.')
                os.makedirs(prjDir + NwxFile.CONTENT_DIR)
            targetFile = NwxFile(f'{prjDir}/nwProject.nwx', **kwargs)
            self.export_from_yw(sourceFile, targetFile)
        elif fileExtension == NwxFile.EXTENSION:
            sourceFile = NwxFile(sourcePath, **kwargs)
            prjDir = f'{srcDir}/../'
            message = sourceFile.read_xml_file()
            if message.startswith(ERROR):
                return message

            root = sourceFile._tree.getroot()
            prj = root.find('project')
            if prj.find('title') is not None:
                title = prj.find('title').text
            elif prj.find('name') is not None:
                title = prj.find('name').text
            else:
                title = 'NewProject'
            fileName = f'{prjDir}{title}{Yw7File.EXTENSION}'
            if os.path.isfile(fileName):
                if self._confirm_overwrite(fileName):
                    os.replace(fileName, f'{fileName}.bak')
                    self.ui.set_info_what(f'Backup file "{os.path.normpath(fileName)}.bak" saved.')
                else:
                    self.ui.set_info_what('Action canceled by user.')
                    return

            targetFile = Yw7File(fileName, **kwargs)
            self.create_yw7(sourceFile, targetFile)
        else:
            self.ui.set_info_how(f'{ERROR}File type of "{os.path.normpath(sourcePath)}" not supported.')
