"""Provide a generic class for novelWriter item file representation.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
from pywriter.pywriter_globals import *


class NwdFile:
    """abstract novelWriter item file representation.
    
    Public methods:
        read() -- read a content file.
        write() -- write a content file.
    """
    EXTENSION = '.nwd'

    def __init__(self, prj, nwItem):
        """Define instance variables.
        
        Positional arguments:
            prj -- NwxFile instance: the novelWriter project represenation.
            nwItem -- NwItem instance associated with the .nwd file.        
        """
        self._prj = prj
        self._nwItem = nwItem
        self._filePath = os.path.dirname(self._prj.filePath) + self._prj.CONTENT_DIR + nwItem.nwHandle + self.EXTENSION
        self._lines = []

    def read(self):
        """Read a content file.
        
        Return a message beginning with the ERROR constant in case of error.
        """
        try:
            with open(self._filePath, 'r', encoding='utf-8') as f:
                self._lines = f.read().split('\n')
                return 'Item data read in.'

        except:
            raise Error(f'Can not read "{norm_path(self._filePath)}".')

    def write(self):
        """Write a content file. 
        
        Return a message beginning with the ERROR constant in case of error.
        """
        lines = [f'%%~name: {self._nwItem.nwName}',
                 f'%%~path: {self._nwItem.nwParent}/{self._nwItem.nwHandle}',
                 f'%%~kind: {self._nwItem.nwClass}/{self._nwItem.nwLayout}',
                 ]
        lines.extend(self._lines)
        text = '\n'.join(lines)
        try:
            with open(self._filePath, 'w', encoding='utf-8') as f:
                f.write(text)
                return 'nwd file saved.'

        except:
            raise Error(f'Can not write "{norm_path(self._filePath)}".')
