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
from pywnw.nwd_novel_file import NwdNovelFile
from pywnw.nwd_world_file import NwdWorldFile
from pywnw.nwd_object_file import NwdObjectFile


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
        self.crCount = 0
        self.itCount = 0
        self.scCount = 0
        self.chCount = 0
        self.chId = None

        self.sceneStatus = kwargs['scene_status']

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
            """Add nodes to the novelWriter project tree of handles.
            """

            for item in content.iter('item'):
                parent = item.attrib.get('parent')

                if parent in node:
                    node[parent][item.attrib.get('handle')] = {}
                    add_nodes(node[parent])

        def get_nodes(handle, handles, subtree):
            """Get a list of file handles, passed as a parameter.
            This is for serializing a project subtree.
            """

            if nwItems[handle].nwType == 'FILE':
                handles.append(handle)

            else:

                for node in subtree[handle]:
                    get_nodes(node, handles, subtree[handle])

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

        # Build a tree of handles.

        nwTree = {'None': {}}
        add_nodes(nwTree)

        # Collect items:

        nwItems = {}

        for node in content.iter('item'):
            item = NwItem()
            handle = item.read(node)

            if not self.nwHandles.add_member(handle):
                return 'ERROR: Invalid handle: ' + handle

            nwItems[handle] = item

        #--- Re-serialize the project tree to get lists of file handles.

        for handle in nwTree['None']:

            if nwItems[handle].nwClass == 'CHARACTER':
                charList = []
                get_nodes(handle, charList, nwTree['None'])

            if nwItems[handle].nwClass == 'WORLD':
                worldList = []
                get_nodes(handle, worldList, nwTree['None'])

            if nwItems[handle].nwClass == 'OBJECT':
                objectList = []
                get_nodes(handle, objectList, nwTree['None'])

            if nwItems[handle].nwClass == 'NOVEL':
                novList = []
                get_nodes(handle, novList, nwTree['None'])

        #--- Get characters.

        crIdsByTitle = {}

        for handle in charList:
            nwdFile = NwdCharacterFile(self, nwItems[handle])
            message = nwdFile.read()

            if message.startswith('ERROR'):
                return message

        for crId in self.characters:
            crIdsByTitle[self.characters[crId].title] = crId

        #--- Get locations.

        lcIdsByTitle = {}

        for handle in worldList:
            nwdFile = NwdWorldFile(self, nwItems[handle])
            message = nwdFile.read()

            if message.startswith('ERROR'):
                return message

        for lcId in self.locations:
            lcIdsByTitle[self.locations[lcId].title] = lcId

        #--- Get items.

        itIdsByTitle = {}

        for handle in objectList:
            nwdFile = NwdObjectFile(self, nwItems[handle])
            message = nwdFile.read()

            if message.startswith('ERROR'):
                return message

        for itId in self.items:
            itIdsByTitle[self.items[itId].title] = itId

        #--- Get chapters and scenes.

        for handle in novList:
            nwdFile = NwdNovelFile(self, nwItems[handle])
            message = nwdFile.read()

            if message.startswith('ERROR'):
                return message

        # Fix scene references.

        for scId in self.scenes:
            characters = []

            for crId in self.scenes[scId].characters:
                characters.append(crIdsByTitle[crId])

            self.scenes[scId].characters = characters

            locations = []

            for lcId in self.scenes[scId].locations:
                locations.append(lcIdsByTitle[lcId])

            self.scenes[scId].locations = locations

            items = []

            for itId in self.scenes[scId].items:
                items.append(itIdsByTitle[itId])

            self.scenes[scId].items = items

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

        def write_entry(parent, entry, red, green, blue):
            """Write an XML entry with RGB values as attributes.
            """
            attrib = {
                'blue': str(blue),
                'green': str(green),
                'red': str(red)
            }
            ET.SubElement(parent, 'entry', attrib).text = entry

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

        #--- Write settings.

        settings = ET.SubElement(root, 'settings')
        status = ET.SubElement(settings, 'status')

        try:
            write_entry(status, self.sceneStatus[0], 230, 230, 230)
            write_entry(status, self.sceneStatus[1], 0, 0, 0)
            write_entry(status, self.sceneStatus[2], 170, 40, 0)
            write_entry(status, self.sceneStatus[3], 240, 140, 0)
            write_entry(status, self.sceneStatus[4], 250, 190, 90)
            write_entry(status, self.sceneStatus[5], 58, 180, 58)

        except IndexError:
            pass

        importance = ET.SubElement(settings, 'importance')
        write_entry(importance, 'None', 220, 220, 220)
        write_entry(importance, 'Minor', 0, 122, 188)
        write_entry(importance, 'Major', 21, 0, 180)

        #--- Write content.

        content = ET.SubElement(root, 'content')

        attrCount = 0
        order = [0]
        # Use a list as a stack for the order within a level

        #--- Write novel folder.

        novelFolderHandle = self.nwHandles.create_member('novelFolderHandle')
        novelFolder = NwItem()
        novelFolder.nwHandle = novelFolderHandle
        novelFolder.nwOrder = order[-1]
        novelFolder.nwParent = 'None'
        novelFolder.nwName = 'Novel'
        novelFolder.nwType = 'ROOT'
        novelFolder.nwClass = 'NOVEL'
        novelFolder.nwExpanded = 'True'
        novelFolder.write(content)

        attrCount += 1
        order[-1] += 1
        # content level

        hasPartLevel = False
        isInChapter = False

        # Add novel items to the folder.

        order.append(0)
        # Level up from content to novel

        for chId in self.srtChapters:

            if self.chapters[chId].chLevel == 1:

                # Begin with a new part.

                hasPartLevel = True
                isInChapter = False

                #--- Write a new folder for this part.

                partFolderHandle = self.nwHandles.create_member(chId + self.chapters[chId].title + 'Folder')
                partFolder = NwItem()
                partFolder.nwHandle = partFolderHandle
                partFolder.nwOrder = order[-1]
                partFolder.nwParent = novelFolderHandle
                partFolder.nwName = self.chapters[chId].title
                partFolder.nwType = 'FOLDER'
                partFolder.nwClass = 'NOVEL'
                partFolder.expanded = 'True'

                partFolder.write(content)

                attrCount += 1
                order[-1] += 1
                # novel level

                order.append(0)
                # Level up from novel to part

                # Put the heading into the part folder.

                partHeadingHandle = self.nwHandles.create_member(chId + self.chapters[chId].title)
                partHeading = NwItem()
                partHeading.nwHandle = partHeadingHandle
                partHeading.nwOrder = order[-1]
                partHeading.nwParent = partFolderHandle
                partHeading.nwName = self.chapters[chId].title
                partHeading.nwType = 'FILE'
                partHeading.nwClass = 'NOVEL'
                partHeading.nwExported = 'True'

                if self.chapters[chId].chType == 0:
                    partHeading.nwExported = 'True'
                    partHeading.nwLayout = 'DOCUMENT'

                else:
                    partHeading.nwExported = 'False'
                    partHeading.nwLayout = 'NOTE'

                partHeading.nwStatus = 'None'
                partHeading.write(content)

                # Add it to the .nwd file.

                nwdFile = NwdNovelFile(self, partHeading)
                nwdFile.add_chapter(chId)
                nwdFile.write()

                attrCount += 1
                order[-1] += 1
                # part level

                order.append(0)
                # Level up from part to chapter

            else:

                # Begin with a new chapter.

                isInChapter = True

                #--- Write a new folder for this chapter.

                chapterFolderHandle = self.nwHandles.create_member(chId + self.chapters[chId].title + 'Folder')
                chapterFolder = NwItem()
                chapterFolder.nwHandle = chapterFolderHandle
                chapterFolder.nwOrder = order[-1]

                if hasPartLevel:
                    chapterFolder.nwParent = partFolderHandle

                else:
                    chapterFolder.nwParent = novelFolderHandle

                chapterFolder.nwName = self.chapters[chId].title
                chapterFolder.nwType = 'FOLDER'
                chapterFolder.expanded = 'True'

                chapterFolder.write(content)

                attrCount += 1
                order[-1] += 1
                # part or novel level

                order.append(0)
                # Level up from part or novel to chapter

                # Put the heading into the folder.

                chapterHeadingHandle = self.nwHandles.create_member(chId + self.chapters[chId].title)
                chapterHeading = NwItem()
                chapterHeading.nwHandle = chapterHeadingHandle
                chapterHeading.nwOrder = order[-1]
                chapterHeading.nwParent = chapterFolderHandle
                chapterHeading.nwName = self.chapters[chId].title
                chapterHeading.nwType = 'FILE'
                chapterHeading.nwClass = 'NOVEL'

                if self.chapters[chId].chType == 0:
                    chapterHeading.nwExported = 'True'
                    chapterHeading.nwLayout = 'DOCUMENT'

                else:
                    chapterHeading.nwExported = 'False'
                    chapterHeading.nwLayout = 'NOTE'

                chapterHeading.nwStatus = 'None'
                chapterHeading.write(content)

                # Add it to the .nwd file.

                nwdFile = NwdNovelFile(self, chapterHeading)
                nwdFile.add_chapter(chId)
                nwdFile.write()

                attrCount += 1
                order[-1] += 1
                # chapter level

            for scId in self.chapters[chId].srtScenes:

                #--- Put a scene into the folder.

                sceneHandle = self.nwHandles.create_member(scId + self.scenes[scId].title)
                scene = NwItem()
                scene.nwHandle = sceneHandle
                scene.nwOrder = order[-1]

                if isInChapter:
                    scene.nwParent = chapterFolderHandle

                else:
                    scene.nwParent = partFolderHandle

                if self.scenes[scId].title:
                    title = self.scenes[scId].title

                else:
                    title = 'Scene ' + str(order[-1] + 1)

                scene.nwName = title
                scene.nwType = 'FILE'
                scene.nwClass = 'NOVEL'

                if self.scenes[scId].status is not None:

                    try:
                        scene.nwStatus = self.sceneStatus[self.scenes[scId].status]

                    except IndexError:
                        scene.nwStatus = self.sceneStatus[-1]

                if self.scenes[scId].isUnused:
                    scene.nwExported = 'False'

                else:
                    scene.nwExported = 'True'

                if self.scenes[scId].isNotesScene or self.scenes[scId].isTodoScene:
                    scene.nwLayout = 'NOTE'

                else:
                    scene.nwLayout = 'DOCUMENT'

                if self.scenes[scId].wordCount:
                    scene.nwWordCount = str(self.scenes[scId].wordCount)

                if self.scenes[scId].letterCount:
                    scene.nwCharCount = str(self.scenes[scId].letterCount)

                scene.write(content)

                # Add it to the .nwd file.

                nwdFile = NwdNovelFile(self, scene)
                nwdFile.add_scene(scId)
                nwdFile.write()

                attrCount += 1
                order[-1] += 1
                # chapter or part level

            order.pop()
            # Level down from chapter to part or from part to novel

        order.pop()
        # Level down from novel to content

        #--- Write character folder.

        characterFolderHandle = self.nwHandles.create_member('characterFolderHandle')
        characterFolder = NwItem()
        characterFolder.nwHandle = characterFolderHandle
        characterFolder.nwOrder = order[-1]
        characterFolder.nwParent = 'None'
        characterFolder.nwName = 'Characters'
        characterFolder.nwType = 'ROOT'
        characterFolder.nwClass = 'CHARACTER'
        characterFolder.nwStatus = 'None'
        characterFolder.nwExpanded = 'True'

        characterFolder.write(content)

        attrCount += 1
        order[-1] += 1

        # Add character items to the folder.

        order.append(0)
        # Level up from world to character

        for crId in self.srtCharacters:

            #--- Put a character into the folder.

            characterHandle = self.nwHandles.create_member(crId + self.characters[crId].title)
            character = NwItem()
            character.nwHandle = characterHandle
            character.nwOrder = order[-1]
            character.nwParent = characterFolderHandle

            if self.characters[crId].fullName:
                character.nwName = self.characters[crId].fullName

            elif self.characters[crId].title:
                character.nwName = self.characters[crId].title

            else:
                character.nwName = 'Character ' + str(order[-1] + 1)

            character.nwType = 'FILE'
            character.nwClass = 'CHARACTER'

            if self.characters[crId].isMajor:
                character.nwStatus = 'Major'

            else:
                character.nwStatus = 'Minor'

            character.nwExported = 'True'
            character.nwLayout = 'NOTE'

            character.write(content)

            # Add it to the .nwd file.

            nwdFile = NwdCharacterFile(self, character)
            nwdFile.add_character(crId)
            nwdFile.write()

            attrCount += 1
            order[-1] += 1
            # character level

        order.pop()
        # Level down from character to content

        #--- Write world folder.

        worldFolderHandle = self.nwHandles.create_member('worldFolderHandle')
        worldFolder = NwItem()
        worldFolder.nwHandle = worldFolderHandle
        worldFolder.nwOrder = order[-1]
        worldFolder.nwParent = 'None'
        worldFolder.nwName = 'Locations'
        worldFolder.nwType = 'ROOT'
        worldFolder.nwClass = 'WORLD'
        worldFolder.nwStatus = 'None'
        worldFolder.nwExpanded = 'True'

        worldFolder.write(content)

        attrCount += 1
        order[-1] += 1
        # content level

        # Add world items to the folder.

        order.append(0)
        # Level up from content to world

        for lcId in self.srtLocations:

            #--- Put a location into the folder.

            locationHandle = self.nwHandles.create_member(lcId + self.locations[lcId].title)
            location = NwItem()
            location.nwHandle = locationHandle
            location.nwOrder = order[-1]
            location.nwParent = worldFolderHandle

            if self.locations[lcId].title:
                title = self.locations[lcId].title

            else:
                title = 'Place ' + str(order[-1] + 1)

            location.nwName = title
            location.nwType = 'FILE'
            location.nwClass = 'WORLD'
            location.nwExported = 'True'
            location.nwLayout = 'NOTE'

            location.write(content)

            # Add it to the .nwd file.

            nwdFile = NwdWorldFile(self, location)
            nwdFile.add_element(lcId)
            nwdFile.write()

            attrCount += 1
            order[-1] += 1
            # world level

        order.pop()
        # Level down from world to to content

        #--- Write object folder.

        objectFolderHandle = self.nwHandles.create_member('objectFolderHandle')
        objectFolder = NwItem()
        objectFolder.nwHandle = objectFolderHandle
        objectFolder.nwOrder = order[-1]
        objectFolder.nwParent = 'None'
        objectFolder.nwName = 'Items'
        objectFolder.nwType = 'ROOT'
        objectFolder.nwClass = 'OBJECT'
        objectFolder.nwStatus = 'None'
        objectFolder.nwExpanded = 'True'

        objectFolder.write(content)

        attrCount += 1
        order[-1] += 1
        # content level

        # Add object items to the folder.

        order.append(0)
        # Level up from content to object

        for itId in self.srtItems:

            #--- Put a item into the folder.

            itemHandle = self.nwHandles.create_member(itId + self.items[itId].title)
            item = NwItem()
            item.nwHandle = itemHandle
            item.nwOrder = order[-1]
            item.nwParent = objectFolderHandle

            if self.items[itId].title:
                title = self.items[itId].title

            else:
                title = 'Place ' + str(order[-1] + 1)

            item.nwName = title
            item.nwType = 'FILE'
            item.nwClass = 'OBJECT'
            item.nwExported = 'True'
            item.nwLayout = 'NOTE'

            item.write(content)

            # Add it to the .nwd file.

            nwdFile = NwdObjectFile(self, item)
            nwdFile.add_element(itId)
            nwdFile.write()

            attrCount += 1
            order[-1] += 1
            # object level

        order.pop()
        # Level down from object to to content

        # Write the content counter.

        content.set('count', str(attrCount))

        #--- Format and write the XML tree.

        indent(root)
        self.tree = ET.ElementTree(root)
        self.tree.write(self.filePath, xml_declaration=True, encoding='utf-8')

        return 'SUCCESS: "' + os.path.normpath(self.filePath) + '" written.'
