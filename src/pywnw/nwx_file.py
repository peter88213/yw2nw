"""Provide a class for novelWriter project file representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import xml.etree.ElementTree as ET
from datetime import datetime

from pywriter.model.novel import Novel
from pywriter.yw.xml_indent import indent

from pywnw.handles import Handles
from pywnw.nw_item import NwItem

from pywnw.nwd_character_file import NwdCharacterFile
from pywnw.nwd_world_file import NwdWorldFile
from pywnw.nwd_novel_file import NwdNovelFile


class NwxFile(Novel):
    """novelWriter project representation.
    """

    EXTENSION = '.nwx'
    DESCRIPTION = 'novelWriter project'
    SUFFIX = ''
    CONTENT_DIR = '/content/'
    CONTENT_EXTENSION = '.nwd'

    NWX_TAG = 'novelWriterXML'
    NWX_ATTR = {
        'appVersion': '1.6-alpha0',
        'hexVersion': '0x010600a0',
        'fileVersion': '1.3',
        'timeStamp': datetime.now().replace(microsecond=0).isoformat(sep=' '),
    }

    def __init__(self, filePath, **kwargs):
        """Extend the superclass constructor,
        defining instance variables.
        """
        Novel.__init__(self, filePath, **kwargs)

        self.tree = None
        self.kwargs = kwargs
        self.nwHandles = Handles()

        self.lcCount = 0
        self.lcIdsByName = {}

        self.crCount = 0
        self.crIdsByTitle = {}

        self.scCount = 0
        self.chCount = 0
        self.chId = None

    def read_xml_file(self):
        """Read the novelWriter XML project file.
        Return a message beginning with SUCCESS or ERROR.
        """

        try:
            self.tree = ET.parse(self.filePath)

        except:
            return 'ERROR: Can not process "' + os.path.normpath(self.filePath) + '".'

        return 'SUCCESS: XML element tree read in.'

    def read(self):
        """Parse the files and store selected properties.
        Return a message beginning with SUCCESS or ERROR.
        Override the superclass method.
        """

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

        #--- Read the XML file, if necessary.

        if self.tree is None:
            message = self.read_xml_file()

            if message.startswith('ERROR'):
                return message

        root = self.tree.getroot()

        # Check file type and version.

        if root.tag != self.NWX_TAG:
            return 'ERROR: This seems not to bee a novelWriter project file.'

        if root.attrib.get('fileVersion') != self.NWX_ATTR['fileVersion']:
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

        for node in content.iter('item'):
            item = NwItem()
            handle = item.read(node)

            if self.nwHandles.add_member(handle):
                nwItems[handle] = item

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

        for handle in charList:
            nwdFile = NwdCharacterFile(self, handle, nwItems[handle])
            message = nwdFile.read()

            if message.startswith('ERROR'):
                return message

        #--- Get locations.

        for handle in locList:
            nwdFile = NwdWorldFile(self, handle, nwItems[handle])
            message = nwdFile.read()

            if message.startswith('ERROR'):
                return message

        #--- Get chapters and scenes.

        for handle in novList:
            scId = None
            nwdFile = NwdNovelFile(self, handle, nwItems[handle])
            message = nwdFile.read()

            if message.startswith('ERROR'):
                return message

        return('SUCCESS')

    def merge(self, source):
        """Copy the yWriter project parts that can be mapped to the novelWriter project.
        Return a message beginning with SUCCESS or ERROR.
        Override the superclass method.
        """
        if source.title is not None:
            self.title = source.title

        else:
            self.title = ''

        if source.desc is not None:
            self.desc = source.desc

        else:
            self.desc = ''

        if source.author is not None:
            self.author = source.author

        else:
            self.author = ''

        if source.scenes is not None:
            self.scenes = source.scenes

        if source.srtChapters != []:
            self.srtChapters = source.srtChapters
            self.chapters = source.chapters

        if source.srtCharacters != []:
            self.srtCharacters = source.srtCharacters
            self.characters = source.characters

        if source.srtLocations != []:
            self.srtLocations = source.srtLocations
            self.locations = source.locations

        if source.srtItems != []:
            self.srtItems = source.srtItems
            self.items = source.items

        return 'SUCCESS'

    def write(self):
        """Write the novelFolder attributes to a new novelWriter project
        consisting of a set of different files.
        Return a message beginning with SUCCESS or ERROR.
        Override the superclass method.
        """

        root = ET.Element(self.NWX_TAG, self.NWX_ATTR)

        #--- Write project metadata.

        xmlPrj = ET.SubElement(root, 'project')

        if self.title:
            title = self.title

        else:
            title = 'New project'

        ET.SubElement(xmlPrj, 'name').text = title
        ET.SubElement(xmlPrj, 'title').text = title

        if self.author:
            authors = self.author.split(',')

        else:
            authors = ['']

        for author in authors:
            ET.SubElement(xmlPrj, 'author').text = author.strip()

        # Omit settings.

        world = ET.SubElement(root, 'settings')

        #--- Write content.

        content = ET.SubElement(root, 'content')
        attrCount = 0
        level0Order = 0

        #--- Write novel folder.

        attrCount += 1
        novelFolderHandle = self.nwHandles.create_member('novelFolderHandle')
        novelFolder = NwItem()
        novelFolder.nwHandle = novelFolderHandle
        novelFolder.nwOrder = level0Order
        novelFolder.nwParent = 'None'
        novelFolder.nwName = 'Novel'
        novelFolder.nwType = 'ROOT'
        novelFolder.nwClass = 'NOVEL'
        novelFolder.nwStatus = 'None'
        novelFolder.nwExpanded = 'True'
        novelFolder.write(content)
        level0Order += 1
        level1Order = 0

        for chId in self.srtChapters:

            # Put a chapter into the folder.

            attrCount += 1
            chapterHandle = self.nwHandles.create_member(chId + self.chapters[chId].title)
            chapter = NwItem()
            chapter.nwHandle = chapterHandle
            chapter.nwOrder = level1Order
            chapter.nwParent = novelFolderHandle
            chapter.write(content)
            level1Order += 1

            for scId in self.chapters[chId].srtScenes:

                # Put a scene into the folder.

                attrCount += 1
                sceneHandle = self.nwHandles.create_member(scId + self.scenes[scId].title)
                scene = NwItem()
                scene.nwHandle = sceneHandle
                scene.nwOrder = level1Order
                scene.nwParent = novelFolderHandle
                scene.write(content)
                level1Order += 1

        #--- Write character folder.

        attrCount += 1
        characterFolderHandle = self.nwHandles.create_member('characterFolderHandle')
        characterFolder = NwItem()
        characterFolder.nwHandle = characterFolderHandle
        characterFolder.nwOrder = level0Order
        characterFolder.nwParent = 'None'
        characterFolder.nwName = 'Characters'
        characterFolder.nwType = 'ROOT'
        characterFolder.nwClass = 'CHARACTER'
        characterFolder.nwStatus = 'None'
        characterFolder.nwExpanded = 'True'
        characterFolder.write(content)
        level0Order += 1
        level1Order = 0

        for crId in self.srtCharacters:

            #--- Put a character into the folder.

            attrCount += 1
            characterHandle = self.nwHandles.create_member(crId + self.characters[crId].title)
            character = NwItem()
            character.nwHandle = characterHandle
            character.nwOrder = level1Order
            character.nwParent = novelFolderHandle
            character.write(content)
            level1Order += 1

        #--- Write world folder.

        attrCount += 1
        worldFolderHandle = self.nwHandles.create_member('worldFolderHandle')
        worldFolder = NwItem()
        worldFolder.nwHandle = worldFolderHandle
        worldFolder.nwOrder = level0Order
        worldFolder.nwParent = 'None'
        worldFolder.nwName = 'Locations'
        worldFolder.nwType = 'ROOT'
        worldFolder.nwClass = 'WORLD'
        worldFolder.nwStatus = 'None'
        worldFolder.nwExpanded = 'True'
        worldFolder.write(content)
        level0Order += 1
        level1Order = 0

        for lcId in self.srtLocations:

            #--- Put a location into the folder.

            attrCount += 1
            locationHandle = self.nwHandles.create_member(lcId + self.locations[lcId].title)
            location = NwItem()
            location.nwHandle = locationHandle
            location.nwOrder = level1Order
            location.nwParent = novelFolderHandle
            location.write(content)
            level1Order += 1

        # Write the content counter.

        content.set('count', str(attrCount))

        #--- Format and write the XML tree.

        indent(root)
        self.tree = ET.ElementTree(root)
        self.tree.write(self.filePath, xml_declaration=True, encoding='utf-8')

        return 'SUCCESS: "' + os.path.normpath(self.filePath) + '" written.'
