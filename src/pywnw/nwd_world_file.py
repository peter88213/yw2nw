"""Provide a class for novelWriter world file representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.model.world_element import WorldElement

from pywnw.nwd_file import NwdFile


class NwdWorldFile(NwdFile):
    """novelWriter world file representation.
    Read yWriter locations from a .nwd file.
    Write yWriter locations to a .nwd file.    
    """

    def __init__(self, prj, nwItem):
        """Extend the superclass constructor,
        defining instance variables.
        """
        NwdFile.__init__(self, prj, nwItem)

        # Customizable tags for characters and locations.

        self.ywAkaKeyword = '%' + prj.kwargs['ywriter_aka_keyword'] + ': '
        self.ywTagKeyword = '%' + prj.kwargs['ywriter_tag_keyword'] + ': '

    def read(self):
        """Parse the files and store selected properties.
        Return a message beginning with SUCCESS or ERROR.
        Extend the superclass method.
        """
        message = NwdFile.read(self)

        if message.startswith('ERROR'):
            return message

        self.prj.lcCount += 1
        lcId = str(self.prj.lcCount)
        self.prj.locations[lcId] = WorldElement()
        self.prj.locations[lcId].title = self.nwItem.nwName
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
                    self.prj.locations[lcId].aka = line.split(':')[1].strip()

                elif line.startswith(self.ywTagKeyword):

                    if self.prj.locations[lcId].tags is None:
                        self.prj.locations[lcId].tags = []

                    self.prj.locations[lcId].tags.append(line.split(':')[1].strip())

                else:
                    continue

            elif line.startswith('@'):

                if line.startswith('@tag'):
                    self.prj.locations[lcId].title = line.split(':')[1].strip().replace('_', ' ')

                else:
                    continue

            else:
                desc.append(line)

        self.prj.locations[lcId].desc = '\n'.join(desc)
        self.prj.srtLocations.append(lcId)
        return('SUCCESS')

    def add_element(self, lcId):
        """Add an element of the story world to the lines list.
        """
        location = self.prj.locations[lcId]

        # Set Heading.

        self.lines.append('# ' + location.title + '\n')

        # Set tag.

        self.lines.append('@tag: ' + location.title.replace(' ', '_'))

        # Set yWriter AKA.

        if location.aka:
            self.lines.append(self.ywAkaKeyword + location.aka)

        # Set yWriter tags.

        if location.tags is not None:

            for tag in location.tags:
                self.lines.append(self.ywTagKeyword + tag)

        # Set yWriter description.

        if location.desc:
            self.lines.append('\n' + location.desc)

        return NwdFile.write(self)
