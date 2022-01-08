"""Provide a class for novelWriter world file representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.model.world_element import WorldElement

from pywnw.nwd_file import NwdFile


class NwdWorldFile(NwdFile):
    """novelWriter location file representation.
    Read yWriter world elements from a .nwd file.
    Write yWriter world elements to a .nwd file.    
    """

    def __init__(self, prj, nwItem):
        """Extend the superclass constructor,
        defining instance variables.
        """
        NwdFile.__init__(self, prj, nwItem)

        # Customizable tags for characters and locations.

        self.weAkaTag = '%' + prj.kwargs['world_element_aka_tag'] + ':'
        self.weTagTag = '%' + prj.kwargs['world_element_tag_tag'] + ':'

    def read(self):
        """Parse the files and store selected properties.
        Return a message beginning with SUCCESS or ERROR.
        Extend the superclass method.
        """

        self.prj.lcCount = 0
        self.prj.lcIdsByName = {}

        #--- Get locations.

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

                if line.startswith(self.weAkaTag):
                    self.prj.locations[lcId].aka = line.split(':')[1].strip()

                elif line.startswith(self.weTagTag):

                    if self.prj.locations[lcId].tags is None:
                        self.prj.locations[lcId].tags = []

                    self.prj.locations[lcId].tags.append(line.split(':')[1].strip())

            elif line.startswith('@'):

                if line.startswith('@tag'):
                    self.prj.locations[lcId].title = line.split(':')[1].strip()

            else:
                desc.append(line)

        self.prj.locations[lcId].desc = '\n'.join(desc)
        self.prj.lcIdsByName[self.prj.locations[lcId].title] = [lcId]
        self.prj.srtLocations.append(lcId)
        return('SUCCESS')

    def add_world_element(self, lcId):
        """Add an element of the story world to the lines list.
        """
        location = self.prj.locations[lcId]

        # Set Heading.

        self.lines.append('# ' + location.title + '\n')

        # Set tag.

        self.lines.append('@tag: ' + location.title)

        # Set yWriter AKA.

        if location.aka:
            self.lines.append(self.weAkaTag + ': ' + location.aka)

        # Set yWriter tags.

        if location.tags is not None:

            for tag in location.tags:
                self.lines.append(self.weTagTag + ': ' + tag)

        # Set yWriter description.

        if location.desc:
            self.lines.append('\n' + location.desc)

        return NwdFile.write(self)
