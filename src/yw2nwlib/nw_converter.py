"""Provide an novelWriter converter class for yWriter.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
from pywriter.pywriter_globals import *
from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywriter.yw.yw7_file import Yw7File
from pywriter.model.novel import Novel
from pywriter.yw.yw7_purge import remove_language_tags
from yw2nwlib.nwx_file import NwxFile


class NwConverter(YwCnvUi):
    """A converter class for yWriter and novelWriter.
    
    Public methods:
        run(sourcePath, **kwargs) -- Create source and target objects and run conversion.
    """

    def export_from_yw(self, source, target):
        """Convert from yWriter project to other file format.

        Positional arguments:
            source -- YwFile subclass instance.
            target -- Any Novel subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Save the new file pathname.

        Error handling:
        - If the conversion fails, newFile is set to None.
        
        Overrides the superclass method.
        """
        self.ui.set_info_what(
            _('Input: {0} "{1}"\nOutput: {2} "{3}"').format(source.DESCRIPTION, norm_path(source.filePath), target.DESCRIPTION, norm_path(target.filePath)))
        try:
            self.check(source, target)
            source.novel = Novel()
            source.read()
            remove_language_tags(source.novel)
            target.novel = source.novel
            target.write()
        except Error as ex:
            message = f'!{str(ex)}'
            self.newFile = None
        else:
            message = f'{_("File written")}: "{norm_path(target.filePath)}".'
            self.newFile = target.filePath
        finally:
            self.ui.set_info_how(message)

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.

        Positional arguments: 
            sourcePath -- str: the source file path.
        
        Required keyword arguments: 
            (see NwxFile)

        Overrides the superclass method.
        """
        if not os.path.isfile(sourcePath):
            self.ui.set_info_how(f'!File "{norm_path(sourcePath)}" not found.')
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
                self.ui.set_info_how(f'!Please exit novelWriter.')
                return

            try:
                os.makedirs(f'{prjDir}{NwxFile.CONTENT_DIR}')
            except FileExistsError:
                extension = '.bak'
                i = 0
                while os.path.isdir(f'{prjDir}{extension}'):
                    extension = f'.bk{i:03}'
                    i += 1
                    if i > 999:
                        self.ui.set_info_how(f'!Unable to back up the project.')
                        return

                os.replace(prjDir, f'{prjDir}{extension}')
                self.ui.set_info_what(f'Backup folder "{norm_path(prjDir)}{extension}" saved.')
                os.makedirs(f'{prjDir}{NwxFile.CONTENT_DIR}')
            targetFile = NwxFile(f'{prjDir}/nwProject.nwx', **kwargs)
            self.export_from_yw(sourceFile, targetFile)
        elif fileExtension == NwxFile.EXTENSION:
            sourceFile = NwxFile(sourcePath, **kwargs)
            prjDir = f'{srcDir}/../'
            sourceFile.read_xml_file()
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
                    self.ui.set_info_what(f'Backup file "{norm_path(fileName)}.bak" saved.')
                else:
                    self.ui.set_info_what('Action canceled by user.')
                    return

            targetFile = Yw7File(fileName, **kwargs)
            self.create_yw7(sourceFile, targetFile)
        else:
            self.ui.set_info_how(f'!File type of "{norm_path(sourcePath)}" not supported.')
