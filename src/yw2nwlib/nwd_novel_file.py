"""Provide a class for novelWriter novel file representation.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import re
from pywriter.pywriter_globals import *
from pywriter.model.scene import Scene
from pywriter.model.chapter import Chapter
from yw2nwlib.nwd_file import NwdFile


class NwdNovelFile(NwdFile):
    """novelWriter novel file representation.
    
    Public methods:
        read() -- read a content file.
        add_scene(scId) -- add a scene to the file content.
        add_chapter(chId) -- add a chapter to the file content.
    """
    _POV_TAG = '@pov: '
    _CHARACTER_TAG = '@char: '
    _LOCATION_TAG = '@location: '
    _ITEM_TAG = '@object: '
    _SYNOPSIS_KEYWORD = 'synopsis:'

    def __init__(self, prj, nwItem):
        """Define instance variables.
        
        Positional arguments:
            prj -- NwxFile instance: the novelWriter project represenation.
            nwItem -- NwItem instance associated with the .nwd file.        

        Required keyword arguments from prj:
            outline_status -- tuple of str: novelWriter status to be converted to yWriter "Outline" scene status.
            draft_status -- tuple of str: novelWriter status to be converted to yWriter "Draft" scene status.
            first_edit_status -- tuple of str: novelWriter status to be converted to yWriter "1st Edit" scene status.
            second_edit_status -- tuple of str: novelWriter status to be converted to yWriter "2nd Edit" scene status.
            done_status -- tuple of str: novelWriter status to be converted to yWriter "Done" scene status.
            ywriter_tag_keyword -- str: keyword for 'tag' pseudo tag in novelWriter, signifying a yWriter tag.     

        Extends the superclass constructor.
        """
        super().__init__(prj, nwItem)

        # Conversion options.
        self.doubleLinebreaks = prj.kwargs['double_linebreaks']

        # Scene status mapping.
        self._outlineStatus = prj.kwargs['outline_status']
        self._draftStatus = prj.kwargs['draft_status']
        self._firstEditStatus = prj.kwargs['first_edit_status']
        self._secondEditStatus = prj.kwargs['second_edit_status']
        self._doneStatus = prj.kwargs['done_status']

        # Customizable tags for general use.
        self._ywTagKeyword = f'%{prj.kwargs["ywriter_tag_keyword"]}: '

        # Headings that divide the file into parts, chapters and scenes.
        # self.partHeadingPrefix = prj.kwargs['part_heading_prefix']
        # self.chapterHeadingPrefix = prj.kwargs['chapter_heading_prefix']
        # self.sceneHeadingPrefix = prj.kwargs['scene_heading_prefix']
        # self.sectionHeadingPrefix = prj.kwargs['section_heading_prefix']

    def _convert_from_yw(self, text, quick=False):
        """Return text, converted from yw7 markup to Markdown.
        
        Positional arguments:
            text -- string to convert.
        
        Optional arguments:
            quick -- bool: if True, apply a conversion mode for one-liners without formatting.
        
        Overrides the superclass method.
        """
        if quick:
            # Just clean up a one-liner without sophisticated formatting.
            if text is None:
                return ''
            else:
                return text

        # Convert italics, bold, and strikethrough.
        MD_REPLACEMENTS = [
            ('[i] ', ' [i]'),
            ('[b] ', ' [b]'),
            ('[s] ', ' [s]'),
            (' [/i]', '[/i] '),
            (' [/b]', '[/b] '),
            (' [/s]', '[/s] '),
            ('[i]', '_'),
            ('[/i]', '_'),
            ('[b]', '**'),
            ('[/b]', '**'),
            ('[s]', '~~'),
            ('[/s]', '~~'),
            ('  ', ' '),
        ]
        if self.doubleLinebreaks:
            MD_REPLACEMENTS.insert(0, ['\n', '\n\n'])
        try:
            for yw, md in MD_REPLACEMENTS:
                text = text.replace(yw, md)
            text = re.sub('\[\/*[h|c|r|u]\d*\]', '', text)
            # Remove highlighting, alignment, and underline tags
        except AttributeError:
            text = ''
        return text

    def _convert_to_yw(self, text):
        """Return text, converted from Markdown to yw7 markup.
        
        Positional arguments:
            text -- string to convert.
        
        Overrides the superclass method.
        """

        # Convert bold, italics, and strikethrough.
        text = re.sub('\*\*(.+?)\*\*', '[b]\\1[/b]', text)
        text = re.sub('\_([^ ].+?[^ ])\_', '[i]\\1[/i]', text)
        text = re.sub('\~\~(.+?)\~\~', '[s]\\1[/s]', text)

        # Text alignment in yWriter is more complicated than it seems
        # at first glance, so don't support it for now.
        # text = re.sub('\>\>(.+?)\<\<\n', '[c]\\1\n[/c]', text)
        # text = re.sub('\>\>(.+?)\<\<', '[c]\\1', text)
        # text = re.sub('\>\>(.+?)\n', '[r]\\1\n[/r]', text)
        # text = re.sub('\>\>(.+?)', '[r]\\1', text)
        # text = text.replace('<<', '')

        MD_REPLACEMENTS = []
        if self.doubleLinebreaks:
            MD_REPLACEMENTS.insert(0, ('\n\n', '\n'))
        try:
            for md, yw in MD_REPLACEMENTS:
                text = text.replace(md, yw)
        except AttributeError:
            text = ''
        return text

    def read(self):
        """Read a content file.
        
        Return a message beginning with the ERROR constant in case of error.
        Extends the superclass method.
        """

        def set_scene_content(scId, contentLines, characters, locations, items, synopsis, tags):
            if scId is not None:
                text = '\n'.join(contentLines)
                self._prj.novel.scenes[scId].sceneContent = self._convert_to_yw(text)
                self._prj.novel.scenes[scId].desc = '\n'.join(synopsis)
                self._prj.novel.scenes[scId].characters = characters
                self._prj.novel.scenes[scId].locations = locations
                self._prj.novel.scenes[scId].items = items
                self._prj.novel.scenes[scId].tags = tags

        #--- Get chapters and scenes.
        scId = None
        super().read()

        # Determine the attibutes for all chapters and scenes included.
        elementType = None
        status = None
        if self._nwItem.nwLayout == 'DOCUMENT' and self._nwItem.nwActive:
            elementType = 0
            # Normal
        elif self._nwItem.nwLayout == 'NOTE':
            elementType = 1
            # Notes
        else:
            elementType = 3
            # Unused
        if self._nwItem.nwStatus in self._outlineStatus:
            status = 1
        elif self._nwItem.nwStatus in self._draftStatus:
            status = 2
        elif self._nwItem.nwStatus in self._firstEditStatus:
            status = 3
        elif self._nwItem.nwStatus in self._secondEditStatus:
            status = 4
        elif self._nwItem.nwStatus in self._doneStatus:
            status = 5
        else:
            status = 1
        characters = []
        locations = []
        items = []
        synopsis = []
        contentLines = []
        tags = []
        inScene = False
        sceneTitle = None
        appendToPrev = None
        for line in self._lines:
            if line.startswith('%%'):
                continue

            elif line.startswith(self._POV_TAG):
                characters.insert(0, line.replace(self._POV_TAG, '').strip().replace('_', ' '))
            elif line.startswith(self._CHARACTER_TAG):
                characters.append(line.replace(self._CHARACTER_TAG, '').strip().replace('_', ' '))
            elif line.startswith(self._LOCATION_TAG):
                locations.append(line.replace(self._LOCATION_TAG, '').strip().replace('_', ' '))
            elif line.startswith(self._ITEM_TAG):
                items.append(line.replace(self._ITEM_TAG, '').strip().replace('_', ' '))
            elif line.startswith('@'):
                continue

            elif line.startswith('%'):
                if line.startswith(self._ywTagKeyword):
                    tags.append(line.split(':', maxsplit=1)[1].strip())
                else:
                    line = line.lstrip('%').lstrip()
                    if line.lower().startswith(self._SYNOPSIS_KEYWORD):
                        synopsis.append(line.split(':', maxsplit=1)[1].strip())
                    pass
            elif line.startswith('###') and self._prj.chId:
                # Set previous scene content.
                set_scene_content(scId, contentLines, characters, locations, items, synopsis, tags)
                scId = None
                characters = []
                locations = []
                items = []
                synopsis = []
                tags = []
                sceneTitle = line.split(' ', maxsplit=1)[1]
                if line.startswith('####'):
                    appendToPrev = True
                else:
                    appendToPrev = None
                inScene = True
            elif line.startswith('#'):
                # Set previous scene content.
                set_scene_content(scId, contentLines, characters, locations, items, synopsis, tags)
                synopsis = []

                # Add a chapter.
                self._prj.chCount += 1
                self._prj.chId = str(self._prj.chCount)
                self._prj.novel.chapters[self._prj.chId] = Chapter()
                self._prj.novel.chapters[self._prj.chId].title = line.split(' ', maxsplit=1)[1]
                self._prj.novel.chapters[self._prj.chId].chType = elementType
                self._prj.novel.srtChapters.append(self._prj.chId)
                if line.startswith('##'):
                    self._prj.novel.chapters[self._prj.chId].chLevel = 0
                else:
                    self._prj.novel.chapters[self._prj.chId].chLevel = 1

                # Prepare the next scene that may be appended without a heading.
                scId = None
                characters = []
                locations = []
                items = []
                tags = []
                sceneTitle = f'Scene {self._prj.scCount + 1}'
                inScene = False
            elif scId is None and not line:
                continue

            elif sceneTitle and scId is None:
                # Write chapter synopsis.
                if synopsis and not inScene:
                    self._prj.novel.chapters[self._prj.chId].desc = '\n'.join(synopsis)
                    synopsis = []
                inScene = True

                # Add a scene.
                self._prj.scCount += 1
                scId = str(self._prj.scCount)
                self._prj.novel.scenes[scId] = Scene()
                self._prj.novel.scenes[scId].status = status
                self._prj.novel.scenes[scId].title = sceneTitle
                self._prj.novel.scenes[scId].scType = elementType
                self._prj.novel.chapters[self._prj.chId].srtScenes.append(scId)
                self._prj.novel.scenes[scId].appendToPrev = appendToPrev
                contentLines = [line]
            elif scId is not None:
                contentLines.append(line)

        # Write the last scene of the file or a chapter synopsis, if there is no scene.
        if scId is not None:
            set_scene_content(scId, contentLines, characters, locations, items, synopsis, tags)
        elif synopsis:
            self._prj.novel.chapters[self._prj.chId].desc = '\n'.join(synopsis)
        return 'Chapters and scenes read in.'

    def add_scene(self, scId):
        """Add a scene to the file content.
        
        Positional arguments:
            scId -- str: scene ID.
        """
        scene = self._prj.novel.scenes[scId]
        if scene.appendToPrev:
            self._lines.append(f'#### {scene.title}\n')
        else:
            self._lines.append(f'### {scene.title}\n')

        # Set point of view and characters.
        if scene.characters is not None:
            isViewpoint = True
            for crId in scene.characters:
                if isViewpoint:
                    self._lines.append(self._POV_TAG + self._prj.novel.characters[crId].title.replace(' ', '_'))
                    isViewpoint = False
                else:
                    self._lines.append(self._CHARACTER_TAG + self._prj.novel.characters[crId].title.replace(' ', '_'))

        # Set locations.
        if scene.locations is not None:
            for lcId in scene.locations:
                self._lines.append(self._LOCATION_TAG + self._prj.novel.locations[lcId].title.replace(' ', '_'))

        # Set items.
        if scene.items is not None:
            for itId in scene.items:
                self._lines.append(self._ITEM_TAG + self._prj.novel.items[itId].title.replace(' ', '_'))

        # Set yWriter tags.
        if scene.tags is not None:
            for tag in scene.tags:
                self._lines.append(self._ywTagKeyword + tag)

        # Set synopsis.
        if scene.desc:
            synopsis = scene.desc.replace('\n', '\t')
            self._lines.append(f'\n% {self._SYNOPSIS_KEYWORD} {synopsis}')

        # Separate the text body by a blank line.
        self._lines.append('\n')

        # Set scene content.
        text = self._convert_from_yw(scene.sceneContent)
        if text:
            self._lines.append(text)

    def add_chapter(self, chId):
        """Add a chapter to the file content.
        
        Positional arguments:
            chId -- str: chapter ID.
        """
        chapter = self._prj.novel.chapters[chId]
        if chapter.chLevel == 0:
            self._lines.append(f'## {chapter.title}\n')
        else:
            self._lines.append(f'# {chapter.title}\n')

        # Set yWriter chapter description.
        if chapter.desc:
            synopsis = chapter.desc.replace('\n', '\t')
            self._lines.append(f'\n% {self._SYNOPSIS_KEYWORD} {synopsis}\n')
