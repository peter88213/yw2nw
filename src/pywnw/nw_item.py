"""Provide a class for novelWriter items.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""


class NwItem():
    """novelWriter item representation."""

    def __init__(self):
        self.nwName = None
        self.nwType = None
        self.nwClass = None
        self.nwStatus = None
        self.nwExported = None
        self.nwLayout = None
