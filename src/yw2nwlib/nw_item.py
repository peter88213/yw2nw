"""Provide a generic strategy class for novelWriter items.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""


class NwItem:
    """Abstract novelWriter item representation.
    
    Public instance variables:
        nwName -- str: name or title.
        nwType -- str: type (ROOT/FOLDER/FILE).
        nwClass -- str: class (NOVEL/CHARACTER/WORLD/OBJECT).
        nwStatus -- str: Scene editing status.
        nwImportance -- str: Character importance (major/minor).
        nwActive -- bool: if True, the item is exported by the application.
        nwLayout -- str: layout (DOCUMENT/NOTE).
        nwCharCount -- int: character count.
        nwWordCount -- int: word count.
        nwParaCount -- (not used for conversion).
        nwCursorPos -- (not used for conversion).
        nwHandle -- str: this item's handle.
        nwOrder -- int: sort order.
        nwParent -- str: the parent item's handle.
    
    File format specific classes inherit from this.
    """

    def __init__(self):
        self.nwName = None
        self.nwType = None
        self.nwClass = None
        self.nwStatus = None
        self.nwImportance = None
        self.nwActive = None
        self.nwLayout = None
        self.nwCharCount = None
        self.nwWordCount = None
        self.nwParaCount = None
        self.nwCursorPos = None
        self.nwHandle = None
        self.nwOrder = None
        self.nwParent = None

