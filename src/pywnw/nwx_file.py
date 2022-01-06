"""Provide a class for novelWriter project file representation.

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

from pywnw.nwd_character_file import NwdCharacterFile
from pywnw.nwd_world_file import NwdWorldFile
from pywnw.nwd_novel_file import NwdNovelFile


class NwxFile(Yw7File):
    """novelWriter project representation.
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

        self.kwargs = kwargs
        self.nwHandles = Handles()

        self.lcCount = 0
        self.lcIdsByName = {}

        self.crCount = 0
        self.crIdsByTitle = {}

        self.scCount = 0
        self.chCount = 0
        self.chId = None

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

        for handle in charList:
            nwdFile = NwdCharacterFile(self, handle, nwItems[handle], **self.kwargs)
            message = nwdFile.read()

            if message.startswith('ERROR'):
                return message

        #--- Get locations.

        for handle in locList:
            nwdFile = NwdWorldFile(self, handle, nwItems[handle], **self.kwargs)
            message = nwdFile.read()

            if message.startswith('ERROR'):
                return message

        #--- Get chapters and scenes.

        for handle in novList:
            scId = None
            nwdFile = NwdNovelFile(self, handle, nwItems[handle], **self.kwargs)
            message = nwdFile.read()

            if message.startswith('ERROR'):
                return message

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
