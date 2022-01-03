"""Provide a class for novelWriter project export.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os

from pywnw.nw_file import NwFile
from pywnw.handle_helper import get_handle
from pywriter.file.file_export import FileExport


class NwProject(FileExport):
    """OpenDocument master document representation."""

    chapterTemplate = '''<text:section text:style-name="Sect1" text:name="${Title}" text:protected="true">
<text:section-source xlink:href="../ChID_${ID}.odt"/>
</text:section>
'''

    def get_chapters(self):
        """Process the chapters and nested scenes.
        Return a list of strings.
        Extend the superclass method by generating subdocuments.
        """
        projectDir = os.path.dirname(self.originalPath)

        if projectDir == '':
            projectDir = '.'

        for chId in self.srtChapters:
            handle = get_handle(self.chapters[chId].title, chId)
            subDocument = NwFile(projectDir + '/content/' + handle + '.nwd')

            subDocument.title = self.title + ' - ChID: ' + chId

            subDocument.desc = self.chapters[chId].title

            if self.chapters[chId].desc:
                subDocument.desc += ('\n' + self.chapters[chId].desc)

            subDocument.author = self.author
            subDocument.fileHeader = self.CONTENT_XML_HEADER

            subDocument.chapters[chId] = self.chapters[chId]
            subDocument.srtChapters = [chId]

            subDocument.locations = self.locations
            subDocument.characters = self.characters
            subDocument.items = self.items

            for scId in self.chapters[chId].srtScenes:
                subDocument.scenes[scId] = self.scenes[scId]

            subDocument.write()

        return FileExport.get_chapters(self)
