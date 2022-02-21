"""Provide a class for novelWriter items.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import xml.etree.ElementTree as ET


class NwItem():
    """novelWriter item representation."""

    def __init__(self):
        self.nwName = None
        self.nwType = None
        self.nwClass = None
        self.nwStatus = None
        self.nwExported = None
        self.nwLayout = None
        self.nwCharCount = None
        self.nwWordCount = None
        self.nwParaCount = None
        self.nwCursorPos = None

        self.nwHandle = None
        self.nwOrder = None
        self.nwParent = None

    def read(self, node):
        """Read a novelWriter node entry from the XML project tree. 
        Return the handle.
        """
        self.nwHandle = node.attrib.get('handle')
        self.nwOrder = int(node.attrib.get('order'))
        self.nwParent = node.attrib.get('parent')

        if node.find('name') is not None:
            self.nwName = node.find('name').text

        if node.find('type') is not None:
            self.nwType = node.find('type').text

        if node.find('class') is not None:
            self.nwClass = node.find('class').text

        if node.find('status') is not None:
            self.nwStatus = node.find('status').text

        if node.find('exported') is not None:
            self.nwExported = node.find('exported').text

        if node.find('layout') is not None:
            self.nwLayout = node.find('layout').text

        return self.nwHandle

    def write(self, parentNode):
        """Write a novelWriter item entry to the XML project tree.
        """
        attrib = {
            'handle': self.nwHandle,
            'order': str(self.nwOrder),
            'parent': self.nwParent
        }
        node = ET.SubElement(parentNode, 'item', attrib)

        if self.nwName is not None:
            ET.SubElement(node, 'name').text = self.nwName

        if self.nwType is not None:
            ET.SubElement(node, 'type').text = self.nwType

        if self.nwClass is not None:
            ET.SubElement(node, 'class').text = self.nwClass

        if self.nwStatus is not None:
            ET.SubElement(node, 'status').text = self.nwStatus

        if self.nwExported is not None:
            ET.SubElement(node, 'exported').text = self.nwExported

        if self.nwLayout is not None:
            ET.SubElement(node, 'layout').text = self.nwLayout

        if self.nwCharCount is not None:
            ET.SubElement(node, 'charCount').text = self.nwCharCount

        if self.nwWordCount is not None:
            ET.SubElement(node, 'wordCount').text = self.nwWordCount

        if self.nwParaCount is not None:
            ET.SubElement(node, 'paraCount').text = self.nwParaCount

        if self.nwCursorPos is not None:
            ET.SubElement(node, 'cursorPos').text = self.nwCursorPos

        return node
