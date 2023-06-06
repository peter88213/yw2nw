"""Provide a class for novelWriter world file representation.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.pywriter_globals import *
from pywriter.model.world_element import WorldElement
from yw2nwlib.nwd_file import NwdFile


class NwdWorldFile(NwdFile):
    """novelWriter world file representation.
    
    Public methods:
        read() -- read a content file.
        add_element(lcId) -- add a location to the file content.
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

        # Customizable tags for characters and locations.
        self._ywAkaKeyword = f'%{prj.kwargs["ywriter_aka_keyword"]}: '
        self._ywTagKeyword = f'%{prj.kwargs["ywriter_tag_keyword"]}: '

    def read(self):
        """Read a content file.
        
        Return a message beginning with the ERROR constant in case of error.
        Extends the superclass method.
        """
        super().read()
        self._prj.lcCount += 1
        lcId = str(self._prj.lcCount)
        self._prj.novel.locations[lcId] = WorldElement()
        self._prj.novel.locations[lcId].title = self._nwItem.nwName
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
                    self._prj.novel.locations[lcId].aka = line.split(':')[1].strip()
                elif line.startswith(self._ywTagKeyword):
                    if self._prj.novel.locations[lcId].tags is None:
                        self._prj.novel.locations[lcId].tags = []
                    self._prj.novel.locations[lcId].tags.append(line.split(':')[1].strip())
                else:
                    continue

            elif line.startswith('@'):
                if line.startswith('@tag'):
                    self._prj.novel.locations[lcId].title = line.split(':')[1].strip().replace('_', ' ')
                else:
                    continue

            else:
                desc.append(line)
        self._prj.novel.locations[lcId].desc = '\n'.join(desc)
        self._prj.novel.srtLocations.append(lcId)
        return 'Location data read in.'

    def add_element(self, lcId):
        """Add a location to the file content.
        
        Positional arguments:
            lcId -- str: location ID.
        """
        location = self._prj.novel.locations[lcId]

        # Set Heading.
        self._lines.append(f'# {location.title}\n')

        # Set tag.
        self._lines.append(f'@tag: {location.title.replace(" ", "_")}')

        # Set yWriter AKA.
        if location.aka:
            self._lines.append(self._ywAkaKeyword + location.aka)

        # Set yWriter tags.
        if location.tags is not None:
            for tag in location.tags:
                self._lines.append(self._ywTagKeyword + tag)

        # Set yWriter description.
        if location.desc:
            self._lines.append(f'\n{location.desc}')
        return super().write()
