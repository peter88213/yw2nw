"""Provide a strategy class for novelWriter items (file format version 1.5).

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import xml.etree.ElementTree as ET
from yw2nwlib.nw_item import NwItem


class NwItemV15(NwItem):
    """novelWriter item representation.
    
    Strategy class for file format version 1.5.
    """

    def read(self, node, master):
        """Read a novelWriter node entry from the XML project tree. 
        
        Positional arguments: 
            node -- ElementTree element instance
        
        Return the handle.
        """
        self.nwHandle = node.attrib.get('handle')
        self.nwOrder = int(node.attrib.get('order'))
        self.nwParent = node.attrib.get('parent')
        self.nwType = node.attrib.get('type')
        self.nwClass = node.attrib.get('class')
        self.nwLayout = node.attrib.get('layout')
        if node.find('name') is not None:
            nameNode = node.find('name')
            self.nwName = nameNode.text
            status = nameNode.attrib.get('status')
            if status is not None:
                self.nwStatus = master.statusLookup[status]
            importance = nameNode.attrib.get('import')
            if importance is not None:
                self.nwImportance = master.importanceLookup[importance]
            isActive = nameNode.attrib.get('active')
            if isActive in ('yes', 'true', 'on'):
                self.nwActive = True
            else:
                self.nwActive = False
        return self.nwHandle

    def write(self, parentNode, master):
        """Write a novelWriter item entry to the XML project tree.
        
        Positional arguments: 
            parentNode -- ElementTree element instance: the new element's parent.

        Return a new ElementTree element instance.
        """
        attrib = {
            'handle': self.nwHandle,
            'parent': self.nwParent,
            'order': str(self.nwOrder),
        }
        node = ET.SubElement(parentNode, 'item', attrib)
        nameNode = ET.SubElement(node, 'name')
        if self.nwName is not None:
            nameNode.text = self.nwName
        if self.nwStatus is not None:
            nameNode.set('status', master.STATUS_IDS[self.nwStatus])
        if self.nwImportance is not None:
            nameNode.set('import', master.IMPORTANCE_IDS[self.nwImportance])
        if self.nwActive is not None:
            if self.nwActive:
                nameNode.set('active', 'yes')
            else:
                nameNode.set('active', 'no')
        if self.nwType is not None:
            node.set('type', self.nwType)
        if self.nwClass is not None:
            node.set('class', self.nwClass)
        if self.nwLayout is not None:
            node.set('layout', self.nwLayout)
        nwMeta = ET.SubElement(node, 'meta')
        if self.nwCharCount is not None:
            nwMeta.set('charCount', self.nwCharCount)
        if self.nwWordCount is not None:
            nwMeta.set('wordCount', self.nwWordCount)
        if self.nwParaCount is not None:
            nwMeta.set('paraCount', self.nwParaCount)
        if self.nwCursorPos is not None:
            nwMeta.set('cursorPos', self.nwCursorPos)
        return node
