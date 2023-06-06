"""Provide a class for novelWriter project file representation.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from pywriter.pywriter_globals import *
from pywriter.file.file import File
from pywriter.yw.xml_indent import indent
from yw2nwlib.handles import Handles
from yw2nwlib.nw_item_v1_5 import NwItemV15
from yw2nwlib.nwd_character_file import NwdCharacterFile
from yw2nwlib.nwd_novel_file import NwdNovelFile
from yw2nwlib.nwd_world_file import NwdWorldFile
from yw2nwlib.nwd_object_file import NwdObjectFile

WRITE_NEW_FORMAT = True


class NwxFile(File):
    """novelWriter project representation.
    
    Public methods:
        read_xml_file() -- read the novelWriter XML project file to the project tree.
        read() -- parse the novelWriter xml and md files and get the instance variables.
        merge(source) -- copy the yWriter project parts that can be mapped to the novelWriter project.
        write() -- write instance variables to the novelWriter files.
    
    Public class variables:
        EXTENSION -- str: file extension of the novelWriter xml file. 
        DESCRIPTION -- str: file description that can be displayed.
        SUFFIX -- str: file name suffix (not applicable).
        CONTENT_DIR -- str: relative path to the "content" directory.
        CONTENT_EXTENSION -- str: extension of the novelWriter markdown files.

    Public instance variables:
        nwHandles -- Handles instance (list of handles with methods).
        kwargs -- keyword arguments, holding settings and options.
        lcCount -- int: number of locations. 
        crCount -- int: number of characters.
        itCount -- int: number of items.
        scCount -- int: number of scenes.
        chCount -- int: number of characters.
        chId -- str: ID of the chapter currently processed.
    
    Reads and writes file format version 1.3.
    Reads file format version 1.4.
    """
    EXTENSION = '.nwx'
    DESCRIPTION = 'novelWriter project'
    SUFFIX = ''
    CONTENT_DIR = '/content/'
    CONTENT_EXTENSION = '.nwd'
    _NWX_TAG = 'novelWriterXML'
    _NWX_ATTR_V1_5 = {
        'appVersion': '2.0.2',
        'hexVersion': '0x020002f0',
        'fileVersion': '1.5',
        'timeStamp': datetime.today().replace(microsecond=0).isoformat(sep=' '),
    }
    _NWD_CLASSES = {
        'CHARACTER':NwdCharacterFile,
        'WORLD':NwdWorldFile,
        'OBJECT':NwdObjectFile,
        'NOVEL':NwdNovelFile
        }
    _TRAILER = ('ARCHIVE', 'TRASH')
    STATUS_IDS = {
            'None': 's000001',
            'Outline': 's000002',
            'Draft': 's000003',
            '1st Edit': 's000004',
            '2nd Edit': 's000005',
            'Done': 's000006',
            }

    IMPORTANCE_IDS = {
            'None': 'i000001',
            'Minor': 'i000002',
            'Major': 'i000003',
            }

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.
        
        Positional arguments:
            filePath -- str: path to the yw7 file.
        
        Required keyword arguments:
            scene_status -- tuple of scene status (emulating an enumeration).    
            major_character_status -- tuple of str: novelWriter status meaning "Major" character importance in yWriter.
            character_notes_heading -- str: heading for novelWriter text that is converted to yWriter character notes.
            character_goals_heading -- str: heading for novelWriter text that is converted to yWriter character goals.
            character_bio_heading -- str: heading for novelWriter text that is converted to yWriter character bio.
            ywriter_aka_keyword -- str: keyword for 'aka' pseudo tag in novelWriter, signifying an alternative name.
            ywriter_tag_keyword -- str: keyword for 'tag' pseudo tag in novelWriter, signifying a yWriter tag.
            outline_status -- tuple of str: novelWriter status to be converted to yWriter "Outline" scene status.
            draft_status -- tuple of str: novelWriter status to be converted to yWriter "Draft" scene status.
            first_edit_status -- tuple of str: novelWriter status to be converted to yWriter "1st Edit" scene status.
            second_edit_status -- tuple of str: novelWriter status to be converted to yWriter "2nd Edit" scene status.
            done_status -- tuple of str: novelWriter status to be converted to yWriter "Done" scene status.
    
        Extends the superclass constructor.
        """
        super().__init__(filePath, **kwargs)
        self._tree = None
        self.kwargs = kwargs
        self.nwHandles = Handles()
        self.lcCount = 0
        self.crCount = 0
        self.itCount = 0
        self.scCount = 0
        self.chCount = 0
        self.chId = None
        self._sceneStatus = kwargs['scene_status']
        self.statusLookup = {}

    def read_xml_file(self):
        """Read the novelWriter XML project file to the project tree.
        
        Return a message beginning with the ERROR constant in case of error.
        """
        try:
            self._tree = ET.parse(self.filePath)
        except:
            raise Error(f'Can not process "{norm_path(self.filePath)}".')

    def read(self):
        """Parse the novelWriter xml and md files and get the instance variables.
        
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """

        #--- Read the XML file, if necessary.
        if self._tree is None:
            self.read_xml_file()
        root = self._tree.getroot()

        #--- Check file type and version; apply strategy pattern for the NwItem class.
        if root.tag != self._NWX_TAG:
            raise Error(f'This seems not to bee a novelWriter project file.')

        if root.attrib.get('fileVersion') != self._NWX_ATTR_V1_5['fileVersion']:
            raise Error(f'Wrong file version (must be {self._NWX_ATTR_V1_5["fileVersion"]}).')

        NwItem = NwItemV15
        self.statusLookup = {}
        xmlStatus = root.find('settings').find('status')
        for xmlStatusEntry in xmlStatus.findall('entry'):
            self.statusLookup[xmlStatusEntry.attrib.get('key')] = xmlStatusEntry.text
        self.importanceLookup = {}
        xmlImportance = root.find('settings').find('importance')
        for xmlImportanceEntry in xmlImportance.findall('entry'):
            self.importanceLookup[xmlImportanceEntry.attrib.get('key')] = xmlImportanceEntry.text

        #--- Read project metadata from the xml element _tree.
        prj = root.find('project')
        if prj.find('title') is not None:
            self.novel.title = prj.find('title').text
        elif prj.find('name') is not None:
            self.novel.title = prj.find('name').text
        authors = []
        for author in prj.iter('author'):
            if author is not None:
                if author.text:
                    authors.append(author.text)
        self.novel.authorName = ', '.join(authors)

        #--- Read project content from the xml element tree.
        # This is a simple variant that processes the flat XML structure
        # without evaluating the items' child/parent relations.
        # Assumptions:
        # - The NOVEL items are arranged in the correct order.
        # - ARCHIVE and TRASH sections are located at the end.
        content = root.find('content')
        for node in content.iter('item'):
            nwItem = NwItem()
            handle = nwItem.read(node, self)
            if not self.nwHandles.add_member(handle):
                raise Error(f'Invalid handle: {handle}')

            if nwItem.nwClass in self._TRAILER:
                # Discard the rest of the scenes, if any.
                break

            if nwItem.nwType != 'FILE':
                continue

            nwdFile = self._NWD_CLASSES[nwItem.nwClass](self, nwItem)
            nwdFile.read()

        # Create reference lists.
        crIdsByTitle = {}
        for crId in self.novel.characters:
            crIdsByTitle[self.novel.characters[crId].title] = crId
        lcIdsByTitle = {}
        for lcId in self.novel.locations:
            lcIdsByTitle[self.novel.locations[lcId].title] = lcId
        itIdsByTitle = {}
        for itId in self.novel.items:
            itIdsByTitle[self.novel.items[itId].title] = itId

        # Fix scene references, replacing titles by IDs.
        for scId in self.novel.scenes:
            characters = []
            for crId in self.novel.scenes[scId].characters:
                characters.append(crIdsByTitle[crId])
            self.novel.scenes[scId].characters = characters
            locations = []
            for lcId in self.novel.scenes[scId].locations:
                locations.append(lcIdsByTitle[lcId])
            self.novel.scenes[scId].locations = locations
            items = []
            for itId in self.novel.scenes[scId].items:
                items.append(itIdsByTitle[itId])
            self.novel.scenes[scId].items = items

        return 'novelWriter data converted to novel structure.'

    def write(self):
        """Write instance variables to the novelWriter files.
        
        Return a message beginning with the ERROR constant in case of error.
        Override the superclass method.
        """

        def write_entry(parent, entry, red, green, blue, map):
            """Write an XML entry with RGB values as attributes.
            """
            attrib = {}
            attrib['key'] = map[entry]
            attrib['count'] = '0'
            attrib['blue'] = str(blue)
            attrib['green'] = str(green)
            attrib['red'] = str(red)
            ET.SubElement(parent, 'entry', attrib).text = entry

        root = ET.Element(self._NWX_TAG, self._NWX_ATTR_V1_5)
        NwItem = NwItemV15

        #--- Write project metadata.
        xmlPrj = ET.SubElement(root, 'project')
        if self.novel.title:
            title = self.novel.title
        else:
            title = 'New project'
        ET.SubElement(xmlPrj, 'name').text = title
        ET.SubElement(xmlPrj, 'title').text = title
        if self.novel.authorName:
            authors = self.novel.authorName.split(',')
        else:
            authors = ['']
        for author in authors:
            ET.SubElement(xmlPrj, 'author').text = author.strip()

        #--- Write settings.
        settings = ET.SubElement(root, 'settings')
        status = ET.SubElement(settings, 'status')
        try:
            write_entry(status, self._sceneStatus[0], 230, 230, 230, self.STATUS_IDS)
            write_entry(status, self._sceneStatus[1], 0, 0, 0, self.STATUS_IDS)
            write_entry(status, self._sceneStatus[2], 170, 40, 0, self.STATUS_IDS)
            write_entry(status, self._sceneStatus[3], 240, 140, 0, self.STATUS_IDS)
            write_entry(status, self._sceneStatus[4], 250, 190, 90, self.STATUS_IDS)
            write_entry(status, self._sceneStatus[5], 58, 180, 58, self.STATUS_IDS)
        except IndexError:
            pass
        importance = ET.SubElement(settings, 'importance')
        write_entry(importance, 'None', 220, 220, 220, self.IMPORTANCE_IDS)
        write_entry(importance, 'Minor', 0, 122, 188, self.IMPORTANCE_IDS)
        write_entry(importance, 'Major', 21, 0, 180, self.IMPORTANCE_IDS)

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
        novelFolder.write(content, self)
        attrCount += 1
        order[-1] += 1
        # content level
        hasPartLevel = False
        isInChapter = False

        # Add novel items to the folder.
        order.append(0)
        # Level up from content to novel
        for chId in self.novel.srtChapters:
            if self.novel.chapters[chId].chLevel == 1:
                # Begin with a new part.
                hasPartLevel = True
                isInChapter = False

                #--- Write a new folder for this part.
                partFolderHandle = self.nwHandles.create_member(f'{chId + self.novel.chapters[chId].title}Folder')
                partFolder = NwItem()
                partFolder.nwHandle = partFolderHandle
                partFolder.nwOrder = order[-1]
                partFolder.nwParent = novelFolderHandle
                partFolder.nwName = self.novel.chapters[chId].title
                partFolder.nwType = 'FOLDER'
                partFolder.nwClass = 'NOVEL'
                partFolder.expanded = 'True'
                partFolder.write(content, self)
                attrCount += 1
                order[-1] += 1
                # novel level
                order.append(0)
                # Level up from novel to part

                # Put the heading into the part folder.
                partHeadingHandle = self.nwHandles.create_member(f'{chId + self.novel.chapters[chId].title}')
                partHeading = NwItem()
                partHeading.nwHandle = partHeadingHandle
                partHeading.nwOrder = order[-1]
                partHeading.nwParent = partFolderHandle
                partHeading.nwName = self.novel.chapters[chId].title
                partHeading.nwType = 'FILE'
                partHeading.nwClass = 'NOVEL'
                partHeading.nwLayout = 'DOCUMENT'
                partHeading.nwActive = True
                if self.novel.chapters[chId].chType == 3:
                    partHeading.nwActive = False
                elif self.novel.chapters[chId].chType in (1, 2):
                    partHeading.nwLayout = 'NOTE'
                partHeading.nwStatus = 'None'
                partHeading.nwImportance = 'None'
                partHeading.write(content, self)

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
                chapterFolderHandle = self.nwHandles.create_member(f'{chId}{self.novel.chapters[chId].title}Folder')
                chapterFolder = NwItem()
                chapterFolder.nwHandle = chapterFolderHandle
                chapterFolder.nwOrder = order[-1]
                if hasPartLevel:
                    chapterFolder.nwParent = partFolderHandle
                else:
                    chapterFolder.nwParent = novelFolderHandle
                chapterFolder.nwName = self.novel.chapters[chId].title
                chapterFolder.nwType = 'FOLDER'
                chapterFolder.expanded = 'True'
                chapterFolder.write(content, self)
                attrCount += 1
                order[-1] += 1
                # part or novel level
                order.append(0)
                # Level up from part or novel to chapter

                # Put the heading into the folder.
                chapterHeadingHandle = self.nwHandles.create_member(f'{chId}{self.novel.chapters[chId].title}')
                chapterHeading = NwItem()
                chapterHeading.nwHandle = chapterHeadingHandle
                chapterHeading.nwOrder = order[-1]
                chapterHeading.nwParent = chapterFolderHandle
                chapterHeading.nwName = self.novel.chapters[chId].title
                chapterHeading.nwType = 'FILE'
                chapterHeading.nwClass = 'NOVEL'
                chapterHeading.nwLayout = 'DOCUMENT'
                chapterHeading.nwActive = True
                if self.novel.chapters[chId].chType == 3:
                    chapterHeading.nwActive = False
                elif self.novel.chapters[chId].chType in (1, 2):
                    chapterHeading.nwLayout = 'NOTE'
                chapterHeading.nwStatus = 'None'
                chapterHeading.nwImportance = 'None'
                chapterHeading.write(content, self)

                # Add it to the .nwd file.
                nwdFile = NwdNovelFile(self, chapterHeading)
                nwdFile.add_chapter(chId)
                nwdFile.write()
                attrCount += 1
                order[-1] += 1
                # chapter level
            for scId in self.novel.chapters[chId].srtScenes:
                #--- Put a scene into the folder.
                sceneHandle = self.nwHandles.create_member(f'{scId}{self.novel.scenes[scId].title}')
                scene = NwItem()
                scene.nwHandle = sceneHandle
                scene.nwOrder = order[-1]
                if isInChapter:
                    scene.nwParent = chapterFolderHandle
                else:
                    scene.nwParent = partFolderHandle
                if self.novel.scenes[scId].title:
                    title = self.novel.scenes[scId].title
                else:
                    title = f'Scene {order[-1] + 1}'
                scene.nwName = title
                scene.nwType = 'FILE'
                scene.nwClass = 'NOVEL'
                if self.novel.scenes[scId].status is not None:
                    try:
                        scene.nwStatus = self._sceneStatus[self.novel.scenes[scId].status]
                    except IndexError:
                        scene.nwStatus = self._sceneStatus[-1]
                scene.nwImportance = 'None'
                scene.nwLayout = 'DOCUMENT'
                scene.nwActive = True
                if self.novel.scenes[scId].scType == 3:
                    scene.nwActive = False
                elif self.novel.scenes[scId].scType in (1, 2):
                    scene.nwLayout = 'NOTE'
                if self.novel.scenes[scId].wordCount:
                    scene.nwWordCount = str(self.novel.scenes[scId].wordCount)
                if self.novel.scenes[scId].letterCount:
                    scene.nwCharCount = str(self.novel.scenes[scId].letterCount)
                scene.write(content, self)

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
        characterFolder.nwImportance = 'None'
        characterFolder.nwExpanded = 'True'
        characterFolder.write(content, self)
        attrCount += 1
        order[-1] += 1

        # Add character items to the folder.
        order.append(0)
        # Level up from world to character
        for crId in self.novel.srtCharacters:
            #--- Put a character into the folder.
            characterHandle = self.nwHandles.create_member(f'{crId}{self.novel.characters[crId].title}')
            character = NwItem()
            character.nwHandle = characterHandle
            character.nwOrder = order[-1]
            character.nwParent = characterFolderHandle
            if self.novel.characters[crId].fullName:
                character.nwName = self.novel.characters[crId].fullName
            elif self.novel.characters[crId].title:
                character.nwName = self.novel.characters[crId].title
            else:
                character.nwName = f'Character {order[-1] + 1}'
            character.nwType = 'FILE'
            character.nwClass = 'CHARACTER'
            character.nwStatus = 'None'
            if self.novel.characters[crId].isMajor:
                character.nwImportance = 'Major'
            else:
                character.nwImportance = 'Minor'
            character.nwActive = True
            character.nwLayout = 'NOTE'
            character.write(content, self)

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
        worldFolder.nwImportance = 'None'
        worldFolder.nwExpanded = 'True'
        worldFolder.write(content, self)
        attrCount += 1
        order[-1] += 1
        # content level

        # Add world items to the folder.
        order.append(0)
        # Level up from content to world
        for lcId in self.novel.srtLocations:
            #--- Put a location into the folder.
            locationHandle = self.nwHandles.create_member(f'{lcId}{self.novel.locations[lcId].title}')
            location = NwItem()
            location.nwHandle = locationHandle
            location.nwOrder = order[-1]
            location.nwParent = worldFolderHandle
            if self.novel.locations[lcId].title:
                title = self.novel.locations[lcId].title
            else:
                title = f'Place {order[-1] + 1}'
            location.nwName = title
            location.nwType = 'FILE'
            location.nwClass = 'WORLD'
            location.nwActive = True
            location.nwLayout = 'NOTE'
            location.nwStatus = 'None'
            location.nwImportance = 'None'
            location.write(content, self)

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
        objectFolder.nwImportance = 'None'
        objectFolder.nwExpanded = 'True'
        objectFolder.write(content, self)
        attrCount += 1
        order[-1] += 1
        # content level

        # Add object items to the folder.
        order.append(0)
        # Level up from content to object
        for itId in self.novel.srtItems:
            #--- Put a item into the folder.
            itemHandle = self.nwHandles.create_member(f'{itId}{self.novel.items[itId].title}')
            item = NwItem()
            item.nwHandle = itemHandle
            item.nwOrder = order[-1]
            item.nwParent = objectFolderHandle
            if self.novel.items[itId].title:
                title = self.novel.items[itId].title
            else:
                title = f'Object {order[-1] + 1}'
            item.nwName = title
            item.nwType = 'FILE'
            item.nwClass = 'OBJECT'
            item.nwActive = True
            item.nwLayout = 'NOTE'
            item.nwStatus = 'None'
            item.nwImportance = 'None'
            item.write(content, self)

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
        self._tree = ET.ElementTree(root)
        self._tree.write(self.filePath, xml_declaration=True, encoding='utf-8')
        return f'"{norm_path(self.filePath)}" written.'
