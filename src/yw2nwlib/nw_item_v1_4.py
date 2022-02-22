"""Provide a strategy class for novelWriter items (file format version 1.4).

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import xml.etree.ElementTree as ET

from yw2nwlib.nw_item import NwItem


class NwItemV14(NwItem):
    """novelWriter item representation.
    
    Strategy class for file format version 1.4.
    """

    def read(self, node):
        """Read a novelWriter node entry from the XML project tree. 
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
            self.nwStatus = nameNode.attrib.get('status')
            self.nwExported = nameNode.attrib.get('exported')          

        return self.nwHandle

    def write(self, parentNode):
        """Write a novelWriter item entry to the XML project tree.
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
            nameNode.set('status', self.nwStatus)

        if self.nwExported is not None:
            nameNode.set('exported', self.nwExported)

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
