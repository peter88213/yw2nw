"""Provide a class for novelWriter object file representation.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.pywriter_globals import *
from pywriter.model.world_element import WorldElement
from yw2nwlib.nwd_file import NwdFile


class NwdObjectFile(NwdFile):
    """novelWriter object file representation.
    
    Public methods:
        read() -- read a content file.
        add_element(itId) -- add an element of the story world to the file content.
    """

    def __init__(self, prj, nwItem):
        """Define instance variables.
        
        Positional arguments:
            prj -- NwxFile instance: the novelWriter project represenation.
            nwItem -- NwItem instance associated with the .nwd file.        

        Required keyword arguments from prj:
            ywriter_aka_keyword -- str: keyword for 'aka' pseudo tag in novelWriter, signifying an alternative name.
            ywriter_tag_keyword -- str: keyword for 'tag' pseudo tag in novelWriter, signifying a yWriter tag.

        Extends the superclass constructor.
        """
        super().__init__(prj, nwItem)

        # Customizable tags for characters and items.
        self._ywAkaKeyword = f'%{prj.kwargs["ywriter_aka_keyword"]}: '
        self._ywTagKeyword = f'%{prj.kwargs["ywriter_tag_keyword"]}: '

    def read(self):
        """Read a content file.
        
        Return a message beginning with the ERROR constant in case of error.
        Extends the superclass method.
        """
        super().read()
        self._prj.lcCount += 1
        itId = str(self._prj.lcCount)
        self._prj.novel.items[itId] = WorldElement()
        self._prj.novel.items[itId].title = self._nwItem.nwName
        desc = []
        for line in self._lines:
            if not line:
                continue

            elif line.startswith('%%'):
                continue

            elif line.startswith('#'):
                continue

            elif line.startswith('%'):
                if line.startswith(self._ywAkaKeyword):
                    self._prj.novel.items[itId].aka = line.split(':')[1].strip()
                elif line.startswith(self._ywTagKeyword):
                    if self._prj.novel.items[itId].tags is None:
                        self._prj.novel.items[itId].tags = []
                    self._prj.novel.items[itId].tags.append(line.split(':')[1].strip())
                else:
                    continue

            elif line.startswith('@'):
                if line.startswith('@tag'):
                    self._prj.novel.items[itId].title = line.split(':')[1].strip().replace('_', ' ')
                else:
                    continue

            else:
                desc.append(line)
        self._prj.novel.items[itId].desc = '\n'.join(desc)
        self._prj.novel.srtItems.append(itId)
        return 'Item data read in.'

    def add_element(self, itId):
        """Add an element of the story world to the file content.
         
        Positional arguments:
            itId -- str: item ID.
       """
        item = self._prj.novel.items[itId]

        # Set Heading.
        self._lines.append(f'# {item.title}\n')

        # Set tag.
        self._lines.append(f'@tag: {item.title.replace(" ", "_")}')

        # Set yWriter AKA.
        if item.aka:
            self._lines.append(self._ywAkaKeyword + item.aka)

        # Set yWriter tags.
        if item.tags is not None:
            for tag in item.tags:
                self._lines.append(self._ywTagKeyword + tag)

        # Set yWriter description.
        if item.desc:
            self._lines.append(f'\n{item.desc}')
        return super().write()
