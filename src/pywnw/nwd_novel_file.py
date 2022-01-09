"""Provide a class for novelWriter novel file representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import re

from pywriter.model.scene import Scene
from pywriter.model.chapter import Chapter

from pywnw.nwd_file import NwdFile


class NwdNovelFile(NwdFile):
    """novelWriter novel file representation.
    Read yWriter chapters and scenes from a .nwd file.
    Write yWriter chapters and scenes to a .nwd file.
    """

    POV_TAG = '@pov: '
    CHARACTER_TAG = '@char: '
    LOCATION_TAG = '@location: '
    SYNOPSIS_KEYWORD = 'synopsis:'

    def __init__(self, prj, nwItem):
        """Extend the superclass constructor,
        defining instance variables.
        """
        NwdFile.__init__(self, prj, nwItem)

        # Conversion options.

        self.doubleLinebreaks = prj.kwargs['double_linebreaks']

        # Scene status mapping.

        self.outlineStatus = prj.kwargs['outline_status']
        self.draftStatus = prj.kwargs['draft_status']
        self.firstEditStatus = prj.kwargs['first_edit_status']
        self.secondEditStatus = prj.kwargs['second_edit_status']
        self.doneStatus = prj.kwargs['done_status']

        # Customizable tags for general use.

        self.ywTagKeyword = '%' + prj.kwargs['ywriter_tag_keyword'] + ': '

        # Headings that divide the file into parts, chapters and scenes.

        # self.partHeadingPrefix = prj.kwargs['part_heading_prefix']
        # self.chapterHeadingPrefix = prj.kwargs['chapter_heading_prefix']
        # self.sceneHeadingPrefix = prj.kwargs['scene_heading_prefix']
        # self.sectionHeadingPrefix = prj.kwargs['section_heading_prefix']

    def convert_from_yw(self, text):
        """Convert yw7 markup to Markdown.
        """
        # Convert italics, bold, and strikethrough.

        MD_REPLACEMENTS = [
            ['[i]', '_'],
            ['[/i]', '_'],
            ['[b]', '**'],
            ['[/b]', '**'],
            ['[s]', '~~'],
            ['[/s]', '~~'],
            ['  ', ' '],
        ]

        if self.doubleLinebreaks:
            MD_REPLACEMENTS[:0] = [['\n', '\n\n']]

        try:

            for r in MD_REPLACEMENTS:
                text = text.replace(r[0], r[1])

            # Remove highlighting, alignment,
            # and underline tags.

            text = re.sub('\[\/*[h|c|r|u]\d*\]', '', text)

        except AttributeError:
            text = ''

        return(text)

    def convert_to_yw(self, text):
        """Convert Markdown to yw7 markup.
        """
        # Convert bold, italics, and strikethrough.

        text = re.sub('\*\*(.+?)\*\*', '[b]\\1[/b]', text)
        text = re.sub('\_([^ ].+?[^ ])\_', '[i]\\1[/i]', text)
        text = re.sub('\~\~(.+?)\~\~', '[s]\\1[/s]', text)

        # Text alignment in yWriter is more complicated than it seems
        # at first glance, so don't support it for now.

        #text = re.sub('\>\>(.+?)\<\<\n', '[c]\\1\n[/c]', text)
        #text = re.sub('\>\>(.+?)\<\<', '[c]\\1', text)
        #text = re.sub('\>\>(.+?)\n', '[r]\\1\n[/r]', text)
        #text = re.sub('\>\>(.+?)', '[r]\\1', text)
        #text = text.replace('<<', '')

        MD_REPLACEMENTS = []

        if self.doubleLinebreaks:
            MD_REPLACEMENTS[:0] = [['\n\n', '\n']]

        try:

            for r in MD_REPLACEMENTS:
                text = text.replace(r[0], r[1])

        except AttributeError:
            text = ''

        return(text)

    def read(self):
        """Parse the files and store selected properties.
        Return a message beginning with SUCCESS or ERROR.
        Extend the superclass method.
        """

        def write_scene_content(scId, contentLines, characters, locations, synopsis, tags):

            if scId is not None:
                text = '\n'.join(contentLines)
                self.prj.scenes[scId].sceneContent = self.convert_to_yw(text)
                self.prj.scenes[scId].desc = '\n'.join(synopsis)
                self.prj.scenes[scId].characters = characters
                self.prj.scenes[scId].locations = locations
                self.prj.scenes[scId].tags = tags

        #--- Get chapters and scenes.

        scId = None

        message = NwdFile.read(self)

        if message.startswith('ERROR'):
            return message

        # Determine the attibutes for all chapters and scenes included.

        chType = None
        isNotesScene = None
        isUnused = None
        status = None

        if self.nwItem.nwLayout == 'DOCUMENT':
            chType = 0
            # Normal

        elif self.nwItem.nwLayout == 'NOTE':
            chType = 1
            # Notes
            isNotesScene = True

        else:
            isUnused = True

        if self.nwItem.nwStatus in self.outlineStatus:
            status = 1

        elif self.nwItem.nwStatus in self.draftStatus:
            status = 2

        elif self.nwItem.nwStatus in self.firstEditStatus:
            status = 3

        elif self.nwItem.nwStatus in self.secondEditStatus:
            status = 4

        elif self.nwItem.nwStatus in self.doneStatus:
            status = 5

        characters = []
        locations = []
        synopsis = []
        contentLines = []
        tags = []
        inScene = False
        sceneTitle = None
        appendToPrev = None

        for line in self.lines:

            if line.startswith('%%'):
                continue

            elif line.startswith(self.POV_TAG):
                characters.insert(0, line.replace(self.POV_TAG, '').strip())

            elif line.startswith(self.CHARACTER_TAG):
                characters.append(line.replace(self.CHARACTER_TAG, '').strip())

            elif line.startswith(self.LOCATION_TAG):
                locations.append(line.replace(self.LOCATION_TAG, '').strip())

            elif line.startswith('@'):
                continue

            elif line.startswith('%'):

                if line.startswith(self.ywTagKeyword):
                    tags.append(line.split(':', maxsplit=1)[1].strip())

                else:
                    line = line.lstrip('%').lstrip()

                    if line.lower().startswith(self.SYNOPSIS_KEYWORD):
                        synopsis.append(line.split(':', maxsplit=1)[1].strip())

                    pass

            elif line.startswith('###') and self.prj.chId:

                # Write previous scene content.

                write_scene_content(scId, contentLines, characters, locations, synopsis, tags)
                scId = None
                characters = []
                locations = []
                synopsis = []
                tags = []
                sceneTitle = line.split(' ', maxsplit=1)[1]

                if line.startswith('####'):
                    appendToPrev = True

                else:
                    appendToPrev = None

                inScene = True

            elif line.startswith('#'):

                # Write previous scene content.

                write_scene_content(scId, contentLines, characters, locations, synopsis, tags)
                synopsis = []

                # Add a chapter.

                self.prj.chCount += 1
                self.prj.chId = str(self.prj.chCount)
                self.prj.chapters[self.prj.chId] = Chapter()
                self.prj.chapters[self.prj.chId].title = line.split(' ', maxsplit=1)[1]
                self.prj.chapters[self.prj.chId].chType = chType
                self.prj.chapters[self.prj.chId].isUnused = isUnused
                self.prj.srtChapters.append(self.prj.chId)

                if line.startswith('##'):
                    self.prj.chapters[self.prj.chId].chLevel = 0

                else:
                    self.prj.chapters[self.prj.chId].chLevel = 1

                # Prepare the next scene that may be appended without a heading.

                scId = None
                characters = []
                locations = []
                tags = []
                sceneTitle = 'Scene ' + str(self.prj.scCount + 1)
                inScene = False

            elif scId is None and not line:
                continue

            elif sceneTitle and scId is None:

                # Write chapter synopsis.

                if not inScene and synopsis != []:
                    self.prj.chapters[self.prj.chId].desc = '\n'.join(synopsis)
                    synopsis = []

                inScene = True

                # Add a scene.

                self.prj.scCount += 1
                scId = str(self.prj.scCount)
                self.prj.scenes[scId] = Scene()
                self.prj.scenes[scId].status = status
                self.prj.scenes[scId].title = sceneTitle
                self.prj.scenes[scId].isNotesScene = isNotesScene
                self.prj.chapters[self.prj.chId].srtScenes.append(scId)
                self.prj.scenes[scId].appendToPrev = appendToPrev
                contentLines = [line]

            elif scId is not None:
                contentLines.append(line)

        # Write the last scene of the file or a chapter synopsis, if there is no scene.

        if scId is not None:
            write_scene_content(scId, contentLines, characters, locations, synopsis, tags)

        elif synopsis != []:
            self.prj.chapters[self.prj.chId].desc = '\n'.join(synopsis)

        return('SUCCESS')

    def add_scene(self, scId):
        """Add a scene to the lines list.
        """
        scene = self.prj.scenes[scId]

        if scene.appendToPrev:
            self.lines.append('#### ' + scene.title + '\n')

        else:
            self.lines.append('### ' + scene.title + '\n')

        # Set point of view and characters.

        if scene.characters is not None:
            isViewpoint = True

            for crId in scene.characters:

                if isViewpoint:
                    self.lines.append(self.POV_TAG + self.prj.characters[crId].title)
                    isViewpoint = False

                else:
                    self.lines.append(self.CHARACTER_TAG + self.prj.characters[crId].title)

        # Set locations.

        if scene.locations is not None:

            for lcId in scene.locations:
                self.lines.append(self.LOCATION_TAG + self.prj.locations[lcId].title)

        # Set yWriter tags.

        if scene.tags is not None:

            for tag in scene.tags:
                self.lines.append(self.ywTagKeyword + tag)

        # Set synopsis.

        if scene.desc:
            self.lines.append('\n% ' + self.SYNOPSIS_KEYWORD + ' ' + scene.desc + '\n')

        # Set scene content.

        text = self.convert_from_yw(scene.sceneContent)

        if text:
            self.lines.append(text)

    def add_chapter(self, chId):
        """Add a chapter to the lines list.
        """
        chapter = self.prj.chapters[chId]

        if chapter.chLevel == 0:
            self.lines.append('## ' + chapter.title + '\n')

        else:
            self.lines.append('# ' + chapter.title + '\n')

        # Set yWriter chapter description.

        if chapter.desc:
            self.lines.append('\n% ' + self.SYNOPSIS_KEYWORD + ' ' + chapter.desc + '\n')
