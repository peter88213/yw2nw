"""Provide a generic strategy class for novelWriter items.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""

class NwItem():
    """Abstract novelWriter item representation.
    
    File format specific classes inherit from this.
    """

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

