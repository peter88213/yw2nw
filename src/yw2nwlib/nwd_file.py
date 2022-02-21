"""Provide a generic class for novelWriter item file representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os

from pywriter.pywriter_globals import ERROR


class NwdFile():
    """novelWriter item file representation.
    """

    EXTENSION = '.nwd'

    def __init__(self, prj, nwItem):
        """Define instance variables.
        """
        self.lines = None
        self.prj = prj
        self.nwItem = nwItem
        self.filePath = os.path.dirname(self.prj.filePath) + self.prj.CONTENT_DIR + nwItem.nwHandle + self.EXTENSION
        self.lines = []

    def read(self):
        """Read a content file. 
        Return a message beginning with the ERROR constant in case of error.
        """

        try:
            with open(self.filePath, 'r', encoding='utf-8') as f:
                self.lines = f.read().split('\n')
                return 'Item data read in.'

        except:
            return f'{ERROR}Can not read "{os.path.normpath(self.filePath)}".'

    def write(self):
        """Write a content file. 
        Return a message beginning with the ERROR constant in case of error.
        """
        lines = [f'%%~name: {self.nwItem.nwName}',
                 f'%%~path: {self.nwItem.nwParent}/{self.nwItem.nwHandle}',
                 f'%%~kind: {self.nwItem.nwClass}/{self.nwItem.nwLayout}',
                 ]
        lines.extend(self.lines)
        text = '\n'.join(lines)

        try:
            with open(self.filePath, 'w', encoding='utf-8') as f:
                f.write(text)
                return 'nwd file saved.'

        except:
            return f'{ERROR}Can not write "{os.path.normpath(self.filePath)}".'
