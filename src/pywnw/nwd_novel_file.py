"""Provide a class for novelWriter novel file representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
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

    def __init__(self, prj, nwItem):
        """Extend the superclass constructor,
        defining instance variables.
        """
        NwdFile.__init__(self, prj, nwItem)

        # Scene status mapping.

        self.outlineStatus = prj.kwargs['outline_status']
        self.draftStatus = prj.kwargs['draft_status']
        self.firstEditStatus = prj.kwargs['first_edit_status']
        self.secondEditStatus = prj.kwargs['second_edit_status']
        self.doneStatus = prj.kwargs['done_status']

        # Headings that divide the file into parts, chapters and scenes.

        # self.partHeadingPrefix = prj.kwargs['part_heading_prefix']
        # self.chapterHeadingPrefix = prj.kwargs['chapter_heading_prefix']
        # self.sceneHeadingPrefix = prj.kwargs['scene_heading_prefix']
        # self.sectionHeadingPrefix = prj.kwargs['section_heading_prefix']

    def read(self):
        """Parse the files and store selected properties.
        Return a message beginning with SUCCESS or ERROR.
        Extend the superclass method.
        """

        def write_scene_content(scId, contentLines):

            if scId is not None:
                text = '\n'.join(contentLines)
                self.prj.scenes[scId].sceneContent = text

        #--- Get chapters and scenes.

        scId = None

        message = NwdFile.read(self)

        if message.startswith('ERROR'):
            return message

        # Determine the attibutes for all chapters and scenes included.

        chType = None
        isUnused = None
        isNotesScene = None
        status = None
        title = None

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

        elif self.nwItem.nwStatus in self.doneEditStatus:
            status = 5

        contentLines = []

        for line in self.lines:

            if line.startswith('%%'):
                continue

            elif line.startswith('@'):
                continue

            elif line.startswith('%'):
                continue

            elif line.startswith('###') and self.prj.chId:

                # Write previous scene.

                write_scene_content(scId, contentLines)
                scId = None

                self.prj.scCount += 1
                scId = str(self.prj.scCount)
                self.prj.scenes[scId] = Scene()
                self.prj.scenes[scId].status = status
                title = line.split(' ', maxsplit=1)[1]
                self.prj.scenes[scId].title = title
                self.prj.scenes[scId].isNotesScene = isNotesScene
                self.prj.chapters[self.prj.chId].srtScenes.append(scId)
                contentLines = [line]

                if line.startswith('####'):
                    self.prj.scenes[scId].appendToPrev = True

            elif line.startswith('#'):

                # Write previous scene.

                write_scene_content(scId, contentLines)
                scId = None

                # Add a chapter.

                self.prj.chCount += 1
                self.prj.chId = str(self.prj.chCount)
                self.prj.chapters[self.prj.chId] = Chapter()
                title = line.split(' ', maxsplit=1)[1]
                self.prj.chapters[self.prj.chId].title = title
                self.prj.chapters[self.prj.chId].chType = chType
                self.prj.chapters[self.prj.chId].isUnused = isUnused

                self.prj.srtChapters.append(self.prj.chId)

                if line.startswith('##'):
                    self.prj.chapters[self.prj.chId].chLevel = 0

                else:
                    self.prj.chapters[self.prj.chId].chLevel = 1

            elif scId is not None:
                contentLines.append(line)

        # Write the last scene of the file.

        write_scene_content(scId, contentLines)
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

        self.lines.append('\n')

        # Set synopsis.

        if scene.desc:
            self.lines.append('% Synopsis: ' + scene.desc + '\n')

        # Set scene content.

        text = scene.sceneContent

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
            self.lines.append('% Synopsis: ' + chapter.desc)
