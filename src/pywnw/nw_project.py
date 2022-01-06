"""Provide a class for novelWriter project representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import xml.etree.ElementTree as ET

from pywriter.yw.yw7_file import Yw7File
from pywriter.model.scene import Scene
from pywriter.model.chapter import Chapter
from pywriter.model.world_element import WorldElement
from pywriter.model.character import Character

from pywnw.handles import Handles
from pywnw.nw_item import NwItem


class NwProject(Yw7File):
    """OpenDocument project representation.
    """

    EXTENSION = '.nwx'
    DESCRIPTION = 'novelWriter project'
    SUFFIX = ''
    CONTENT_DIR = '/content/'
    CONTENT_EXTENSION = '.nwd'

    NWX_TAG = 'novelWriterXML'
    NWX_VERSION = '1.3'

    def __init__(self, filePath, **kwargs):
        """Extend the superclass constructor,
        defining instance variables.
        """
        Yw7File.__init__(self, filePath, **kwargs)
        self.nwHandles = Handles()

        # Headings that divide the file into parts, chapters and scenes.

        # self.partHeadingPrefix = kwargs['part_heading_prefix']
        # self.chapterHeadingPrefix = kwargs['chapter_heading_prefix']
        # self.sceneHeadingPrefix = kwargs['scene_heading_prefix']
        # self.sectionHeadingPrefix = kwargs['section_heading_prefix']

        # Scene status mapping.

        self.outlineStatus = kwargs['outline_status']
        self.draftStatus = kwargs['draft_status']
        self.firstEditStatus = kwargs['first_edit_status']
        self.secondEditStatus = kwargs['second_edit_status']
        self.doneStatus = kwargs['done_status']

        # Customizable Character importance.

        self.majorCharacterStatus = kwargs['major_character_status']

        # Headings that divide the character sheet into sections.

        self.characterNotesHeading = kwargs['character_notes_heading']
        self.characterGoalsHeading = kwargs['character_goals_heading']
        self.characterBioHeading = kwargs['character_bio_heading']

        # Customizable tags for characters and locations.

        self.weAkaTag = '%' + kwargs['world_element_aka_tag'] + ':'
        self.weTagTag = '%' + kwargs['world_element_tag_tag'] + ':'

    def read(self):
        """Parse the files and store selected properties.
        Return a message beginning with SUCCESS or ERROR.
        Override the superclass method.
        """

        def read_file(handle):
            """Read a content file. 
            Return the content as a list of lines.
            On error, return an error message instead.
            """
            filePath = os.path.dirname(self.filePath) + self.CONTENT_DIR + handle + self.CONTENT_EXTENSION

            try:
                with open(filePath, 'r', encoding='utf-8') as f:
                    lines = f.read().split('\n')

                return lines

            except:
                return 'ERROR: Can not read "' + os.path.normpath(filePath) + '".'

        def add_nodes(node):
            """Add nodes to the novelWriter project tree.
            This is for de-serializing the project tree. 
            """

            for item in content.iter('item'):
                parent = item.attrib.get('parent')

                if parent in node:
                    node[parent][item.attrib.get('handle')] = {}
                    add_nodes(node[parent])

        def get_nodes(id, list, subtree):
            """Get a list of handles, passed as a parameter.
            This is for serializing a project subtree.
            """

            if nwItems[id].nwType == 'FILE':
                list.append(id)

            else:

                for subId in subtree[id]:
                    get_nodes(subId, list, subtree[id])

        def write_scene_content(scId, contentLines):

            if scId is not None:
                text = '\n'.join(contentLines)
                self.scenes[scId].sceneContent = text

        #--- Read the XML file, if necessary.

        if self.tree is None:
            message = self.read_xml_file()

            if message.startswith('ERROR'):
                return message

        root = self.tree.getroot()

        # Check file type and version.

        if root.tag != self.NWX_TAG:
            return 'ERROR: This seems not to bee a novelWriter project file.'

        if root.attrib.get('fileVersion') != self.NWX_VERSION:
            return 'ERROR: Wrong file version (must be ' + self.NWX_VERSION + ').'

        #--- Read project metadata from the xml element tree.

        prj = root.find('project')

        if prj.find('title') is not None:
            self.title = prj.find('title').text

        elif prj.find('name') is not None:
            self.title = prj.find('name').text

        authors = []

        for author in prj.iter('author'):
            authors.append(author.text)

        self.author = ', '.join(authors)

        #--- Read project content from the xml element tree.

        content = root.find('content')

        # De-serialize the project tree.

        nwTree = {'None': {}}
        add_nodes(nwTree)

        # Collect items:

        nwItems = {}

        for item in content.iter('item'):
            handle = item.attrib.get('handle')

            if self.nwHandles.add_member(handle):
                nwItems[handle] = NwItem()

                if item.find('name') is not None:
                    nwItems[handle].nwName = item.find('name').text

                if item.find('type') is not None:
                    nwItems[handle].nwType = item.find('type').text

                if item.find('class') is not None:
                    nwItems[handle].nwClass = item.find('class').text

                if item.find('status') is not None:
                    nwItems[handle].nwStatus = item.find('status').text

                if item.find('exported') is not None:
                    nwItems[handle].nwExported = item.find('exported').text

                if item.find('layout') is not None:
                    nwItems[handle].nwLayout = item.find('layout').text

            else:
                return 'ERROR: Invalid handle: ' + item.attrib.get('handle')

        #--- Re-serialize the project tree to get lists.

        for id in nwTree['None']:

            if nwItems[id].nwClass == 'CHARACTER':
                charList = []
                get_nodes(id, charList, nwTree['None'])

            if nwItems[id].nwClass == 'WORLD':
                locList = []
                get_nodes(id, locList, nwTree['None'])

            if nwItems[id].nwClass == 'NOVEL':
                novList = []
                get_nodes(id, novList, nwTree['None'])

        #--- Get characters.

        crCount = 0
        crIdsByTitle = {}

        for handle in charList:
            lines = read_file(handle)

            # Catch error message.

            if isinstance(lines, str):
                return lines

            crCount += 1
            crId = str(crCount)
            self.characters[crId] = Character()
            self.characters[crId].fullName = nwItems[handle].nwName
            self.characters[crId].title = nwItems[handle].nwName
            desc = []
            bio = []
            goals = []
            notes = []

            section = 'desc'

            for line in lines:

                if line == '':
                    continue

                elif line.startswith('%%'):
                    continue

                elif line.startswith('#'):
                    section = 'desc'

                    if line.startswith(self.characterBioHeading):
                        section = 'bio'

                    elif line.startswith(self.characterGoalsHeading):
                        section = 'goals'

                    elif line.startswith(self.characterNotesHeading):
                        section = 'notes'

                elif line.startswith('@'):

                    if line.startswith('@tag'):
                        self.characters[crId].title = line.split(':')[1].strip()

                elif line.startswith('%'):

                    if line.startswith(self.weAkaTag):
                        self.characters[crId].aka = line.split(':')[1].strip()

                    elif line.startswith(self.weTagTag):

                        if self.characters[crId].tags is None:
                            self.characters[crId].tags = []

                        self.characters[crId].tags.append(line.split(':')[1].strip())

                elif section == 'desc':
                    desc.append(line)

                elif section == 'bio':
                    bio.append(line)

                elif section == 'goals':
                    goals.append(line)

                elif section == 'notes':
                    notes.append(line)

            self.characters[crId].desc = '\n'.join(desc)
            self.characters[crId].bio = '\n'.join(bio)
            self.characters[crId].goals = '\n'.join(goals)
            self.characters[crId].notes = '\n'.join(notes)

            if nwItems[handle].nwStatus in self.majorCharacterStatus:
                self.characters[crId].isMajor = True

            else:
                self.characters[crId].isMajor = False

            crIdsByTitle[self.characters[crId].title] = [crId]
            self.srtCharacters.append(crId)

        #--- Get locations.

        lcCount = 0
        lcIdsByName = {}

        for handle in locList:
            lines = read_file(handle)

            # Catch error message.

            if isinstance(lines, str):
                return lines

            lcCount += 1
            lcId = str(lcCount)
            self.locations[lcId] = WorldElement()
            self.locations[lcId].title = nwItems[handle].nwName
            desc = []

            for line in lines:

                if line == '':
                    continue

                elif line.startswith('%%'):
                    continue

                elif line.startswith('#'):
                    continue

                elif line.startswith('%'):

                    if line.startswith(self.weAkaTag):
                        self.locations[lcId].aka = line.split(':')[1].strip()

                    elif line.startswith(self.weTagTag):

                        if self.locations[lcId].tags is None:
                            self.locations[lcId].tags = []

                        self.locations[lcId].tags.append(line.split(':')[1].strip())

                elif line.startswith('@'):

                    if line.startswith('@tag'):
                        self.locations[lcId].title = line.split(':')[1].strip()

                else:
                    desc.append(line)

            self.locations[lcId].desc = '\n'.join(desc)
            lcIdsByName[self.locations[lcId].title] = [lcId]
            self.srtLocations.append(lcId)

        #--- Get chapters and scenes.

        scCount = 0
        chCount = 0
        chId = None

        for handle in novList:
            # print(nwItems[handle].nwName)
            scId = None
            lines = read_file(handle)

            # Catch error message.

            if isinstance(lines, str):
                return lines

            # Determine the attibutes for all chapters and scenes included.

            chType = None
            isUnused = None
            isNotesScene = None
            status = None
            title = None

            if nwItems[handle].nwLayout == 'DOCUMENT':
                chType = 0
                # Normal

            elif nwItems[handle].nwLayout == 'NOTE':
                chType = 1
                # Notes
                isNotesScene = True

            else:
                isUnused = True

            if nwItems[handle].nwStatus in self.outlineStatus:
                status = 1

            elif nwItems[handle].nwStatus in self.draftStatus:
                status = 2

            elif nwItems[handle].nwStatus in self.firstEditStatus:
                status = 3

            elif nwItems[handle].nwStatus in self.secondEditStatus:
                status = 4

            elif nwItems[handle].nwStatus in self.doneEditStatus:
                status = 5

            contentLines = []

            for line in lines:

                if line.startswith('%%'):
                    continue

                elif line.startswith('@'):

                    if line.startswith('@tag'):
                        self.characters[crId].title = line.split(':')[1].strip()

                elif line.startswith('%'):

                    if line.startswith(self.weAkaTag):
                        self.characters[crId].aka = line.split(':')[1].strip()

                    elif line.startswith(self.weTagTag):

                        if self.characters[crId].tags is None:
                            self.characters[crId].tags = []

                        self.characters[crId].tags.append(line.split(':')[1].strip())

                elif line.startswith('###') and chId:

                    # Write previous scene.

                    write_scene_content(scId, contentLines)
                    scId = None

                    scCount += 1
                    scId = str(scCount)
                    self.scenes[scId] = Scene()
                    self.scenes[scId].status = status
                    title = line.split(' ', maxsplit=1)[1]
                    self.scenes[scId].title = title
                    self.chapters[chId].srtScenes.append(scId)
                    contentLines = [line]

                    if line.startswith('####'):
                        self.scenes[scId].appendToPrev = True

                elif line.startswith('#'):

                    # Write previous scene.

                    write_scene_content(scId, contentLines)
                    scId = None

                    # Add a chapter.

                    chCount += 1
                    chId = str(chCount)
                    self.chapters[chId] = Chapter()
                    title = line.split(' ', maxsplit=1)[1]
                    self.chapters[chId].title = title
                    self.chapters[chId].chType = chType
                    self.chapters[chId].isUnused = isUnused

                    self.srtChapters.append(chId)

                    if line.startswith('##'):
                        self.chapters[chId].chLevel = 0

                    else:
                        self.chapters[chId].chLevel = 1

                elif scId is not None:
                    contentLines.append(line)

            # Write the last scene of the file.

            write_scene_content(scId, contentLines)

        return('SUCCESS')

    def read_xml_file(self):
        """Read the novelWriter XML project file.
        Return a message beginning with SUCCESS or ERROR.
        """

        try:
            self.tree = ET.parse(self.filePath)

        except:
            return 'ERROR: Can not process "' + os.path.normpath(self.filePath) + '".'

        return 'SUCCESS: XML element tree read in.'
