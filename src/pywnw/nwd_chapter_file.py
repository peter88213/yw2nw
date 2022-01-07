"""Provide a class for novelWriter part/chapter file representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywnw.nwd_file import NwdFile


class NwdChapterFile(NwdFile):
    """novelWriter part/chapter file representation.
    """

    def write(self, chId):
        """Write a content file. 
        Return a message beginning with SUCCESS or ERROR.
        """
        chapter = self.prj.chapters[chId]

        if chapter.chLevel == 0:
            self.lines.append('## ' + chapter.title + '\n')

        else:
            self.lines.append('# ' + chapter.title + '\n')

        # Set yWriter chapter description.

        if chapter.desc:
            self.lines.append('% Synopsis: ' + chapter.desc)

        return NwdFile.write(self)
