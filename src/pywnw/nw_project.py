"""Provide a class for novelWriter project representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import xml.etree.ElementTree as ET

from pywriter.model.novel import Novel
from pywriter.model.scene import Scene
from pywriter.model.chapter import Chapter
from pywriter.model.world_element import WorldElement
from pywriter.model.character import Character

from pywnw.handles import Handles
from pywnw.nw_item import NwItem


class NwProject(Novel):
    """OpenDocument project representation.
    """

    EXTENSION = '.nwx'
    DESCRIPTION = 'novelWriter project'
    SUFFIX = ''
    CONTENT_DIR = '/content/'
    CONTENT_EXTENSION = '.nwd'

    NWX_TAG = 'novelWriterXML'
    NWX_VERSION = '1.3'

    MAJOR_CHARACTER_TAGS = ['Major', 'Main']

    def __init__(self, filePath, **kwargs):
        """Extend the superclass constructor,
        defining instance variables.
        """
        Novel.__init__(self, filePath, **kwargs)
        self.nwHandles = Handles()
        self.tree = None

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
                    lines = f.readlines()

                return lines

            except:
                return 'ERROR: Can not read "' + os.path.normpath(filePath) + '".'

        def add_nodes(node):
            """Add nodes to the novelWriter project tree.
            This is de-serializing the project tree. 
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

        # Read the XML file.

        try:
            self.tree = ET.parse(self.filePath)

        except:
            return 'ERROR: Can not process "' + os.path.normpath(self.filePath) + '".'

        root = self.tree.getroot()
        sceneCount = 0
        chapterCount = 0

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
                    nwItems[handle].doExport = item.find('exported').text

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
        crIdsByName = {}

        for handle in charList:
            lines = read_file(handle)

            if isinstance(lines, str):
                return lines

            crCount += 1
            crId = str(crCount)
            self.characters[crId] = Character()
            self.characters[crId].fullName = nwItems[handle].nwName
            self.characters[crId].name = nwItems[handle].nwName
            description = []

            for line in lines:

                if line == '\n':
                    continue

                if line.startswith('%%'):
                    continue

                if line.startswith('#'):
                    continue

                if line.startswith('@'):

                    if line.startswith('@tag'):
                        self.characters[crId].name = line.split(':')[1].strip()

                else:
                    description.append(line)

            self.characters[crId].desc = '\n'.join(description)

            if nwItems[handle].nwStatus in self.MAJOR_CHARACTER_TAGS:
                self.characters[crId].isMajor = True

            else:
                self.characters[crId].isMajor = False

            crIdsByName[self.characters[crId].name] = [crId]
            self.srtCharacters.append(crId)

        #--- Get locations.

        lcCount = 0
        lcIdsByName = {}

        for handle in locList:
            lines = read_file(handle)

            if isinstance(lines, str):
                return lines

            lcCount += 1
            lcId = str(lcCount)
            self.locations[lcId] = WorldElement()
            self.locations[lcId].title = nwItems[handle].nwName
            description = []

            for line in lines:

                if line == '\n':
                    continue

                if line.startswith('%%'):
                    continue

                if line.startswith('#'):
                    continue

                if line.startswith('@'):

                    if line.startswith('@tag'):
                        self.locations[lcId].title = line.split(':')[1].strip()

                else:
                    description.append(line)

            self.locations[lcId].desc = '\n'.join(description)
            lcIdsByName[self.locations[lcId].title] = [lcId]
            self.srtLocations.append(lcId)

        self.chapters['1'] = Chapter()
        self.srtChapters = ['1']

        for id in novList:
            print(nwItems[id].nwName + '\t' + nwItems[id].nwType)

        return('SUCCESS')
