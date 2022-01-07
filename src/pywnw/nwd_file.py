"""Provide a generic class for novelWriter item file representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os


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
        Return a message beginning with SUCCESS or ERROR.
        """

        try:
            with open(self.filePath, 'r', encoding='utf-8') as f:
                self.lines = f.read().split('\n')

            return 'SUCCESS'

        except:
            return 'ERROR: Can not read "' + os.path.normpath(self.filePath) + '".'

    def write(self):
        """Write a content file. 
        Return a message beginning with SUCCESS or ERROR.
        """
        lines = ['%%~name: ' + self.nwItem.nwName,
                 '%%~path: ' + self.nwItem.nwParent + '/' + self.nwItem.nwHandle,
                 '%%~kind: ' + self.nwItem.nwClass + '/' + self.nwItem.nwLayout,
                 ]
        lines.extend(self.lines)
        text = '\n'.join(lines)

        try:
            with open(self.filePath, 'w', encoding='utf-8') as f:
                f.write(text)

            return 'SUCCESS'

        except:
            return 'ERROR: Can not write "' + os.path.normpath(self.filePath) + '".'
