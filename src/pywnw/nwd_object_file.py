"""Provide a class for novelWriter object file representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.pywriter_globals import ERROR
from pywriter.model.world_element import WorldElement

from pywnw.nwd_file import NwdFile


class NwdObjectFile(NwdFile):
    """novelWriter object file representation.
    Read yWriter items from a .nwd file.
    Write yWriter items to a .nwd file.    
    """

    def __init__(self, prj, nwItem):
        """Extend the superclass constructor,
        defining instance variables.
        """
        super().__init__(prj, nwItem)

        # Customizable tags for characters and items.

        self.ywAkaKeyword = f'%{prj.kwargs["ywriter_aka_keyword"]}: '
        self.ywTagKeyword = f'%{prj.kwargs["ywriter_tag_keyword"]}: '

    def read(self):
        """Parse the files and store selected properties.
        Return a message beginning with the ERROR constant in case of error.
        Extend the superclass method.
        """
        message = super().read()

        if message.startswith(ERROR):
            return message

        self.prj.lcCount += 1
        itId = str(self.prj.lcCount)
        self.prj.items[itId] = WorldElement()
        self.prj.items[itId].title = self.nwItem.nwName
        desc = []

        for line in self.lines:

            if line == '':
                continue

            elif line.startswith('%%'):
                continue

            elif line.startswith('#'):
                continue

            elif line.startswith('%'):

                if line.startswith(self.ywAkaKeyword):
                    self.prj.items[itId].aka = line.split(':')[1].strip()

                elif line.startswith(self.ywTagKeyword):

                    if self.prj.items[itId].tags is None:
                        self.prj.items[itId].tags = []

                    self.prj.items[itId].tags.append(line.split(':')[1].strip())

                else:
                    continue

            elif line.startswith('@'):

                if line.startswith('@tag'):
                    self.prj.items[itId].title = line.split(':')[1].strip().replace('_', ' ')

                else:
                    continue

            else:
                desc.append(line)

        self.prj.items[itId].desc = '\n'.join(desc)
        self.prj.srtItems.append(itId)
        return 'Item data read in.'

    def add_element(self, itId):
        """Add an element of the story world to the lines list.
        """
        item = self.prj.items[itId]

        # Set Heading.

        self.lines.append(f'# {item.title}\n')

        # Set tag.

        self.lines.append(f'@tag: {item.title.replace(" ", "_")}')

        # Set yWriter AKA.

        if item.aka:
            self.lines.append(self.ywAkaKeyword + item.aka)

        # Set yWriter tags.

        if item.tags is not None:

            for tag in item.tags:
                self.lines.append(self.ywTagKeyword + tag)

        # Set yWriter description.

        if item.desc:
            self.lines.append(f'\n{item.desc}')

        return super().write()
