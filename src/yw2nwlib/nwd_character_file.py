"""Provide a class for novelWriter character file representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.pywriter_globals import ERROR
from pywriter.model.character import Character

from yw2nwlib.nwd_file import NwdFile


class NwdCharacterFile(NwdFile):
    """novelWriter character file representation.
    Read yWriter characters from a .nwd file.
    Write yWriter characters to a .nwd file.    
    """

    def __init__(self, prj, nwItem):
        """Extend the superclass constructor,
        defining instance variables.
        """
        super().__init__(prj, nwItem)

        # Customizable Character importance.

        self.majorCharacterStatus = prj.kwargs['major_character_status']

        # Headings that divide the character sheet into sections.

        self.characterNotesHeading = prj.kwargs['character_notes_heading']
        self.characterGoalsHeading = prj.kwargs['character_goals_heading']
        self.characterBioHeading = prj.kwargs['character_bio_heading']

        # Customizable tags for characters and locations.

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

        self.prj.crCount += 1
        crId = str(self.prj.crCount)
        self.prj.characters[crId] = Character()
        self.prj.characters[crId].fullName = self.nwItem.nwName
        self.prj.characters[crId].title = self.nwItem.nwName
        desc = []
        bio = []
        goals = []
        notes = []

        section = 'desc'

        for line in self.lines:

            if not line:
                continue

            elif line.startswith('%%'):
                continue

            elif line.startswith('#'):
                section = 'desc'

                if line.startswith(self.characterBioHeading):
                    section = 'bio'

                elif line.startswith(self.characterGoalsHeading):
                    section = 'goals'

                elif line.startswith(self.characterNotesHeading):
                    section = 'notes'

            elif line.startswith('@'):

                if line.startswith('@tag'):
                    self.prj.characters[crId].title = line.split(':')[1].strip().replace('_', ' ')

            elif line.startswith('%'):

                if line.startswith(self.ywAkaKeyword):
                    self.prj.characters[crId].aka = line.split(':')[1].strip()

                elif line.startswith(self.ywTagKeyword):

                    if self.prj.characters[crId].tags is None:
                        self.prj.characters[crId].tags = []

                    self.prj.characters[crId].tags.append(line.split(':')[1].strip())

            elif section == 'desc':
                desc.append(line)

            elif section == 'bio':
                bio.append(line)

            elif section == 'goals':
                goals.append(line)

            elif section == 'notes':
                notes.append(line)

        self.prj.characters[crId].desc = '\n'.join(desc)
        self.prj.characters[crId].bio = '\n'.join(bio)
        self.prj.characters[crId].goals = '\n'.join(goals)
        self.prj.characters[crId].notes = '\n'.join(notes)

        if self.nwItem.nwStatus in self.majorCharacterStatus:
            self.prj.characters[crId].isMajor = True

        else:
            self.prj.characters[crId].isMajor = False

        self.prj.srtCharacters.append(crId)
        return 'Character data read in.'

    def add_character(self, crId):
        """Add a character to the lines list.
        """
        character = self.prj.characters[crId]

        # Set Heading.

        if character.fullName:
            title = character.fullName

        else:
            title = character.title

        self.lines.append(f'# {title}\n')

        # Set tag.

        self.lines.append(f'@tag: {character.title.replace(" ", "_")}')

        # Set yWriter AKA.

        if character.aka:
            self.lines.append(self.ywAkaKeyword + character.aka)

        # Set yWriter tags.

        if character.tags is not None:

            for tag in character.tags:
                self.lines.append(self.ywTagKeyword + tag)

        # Set yWriter description.

        if character.desc:
            self.lines.append(f'\n{character.desc}')

        # Set yWriter bio.

        if character.bio:
            self.lines.append(f'\n{self.characterBioHeading}')
            self.lines.append(character.bio)

        # Set yWriter goals.

        if character.goals:
            self.lines.append(f'\n{self.characterGoalsHeading}')
            self.lines.append(character.goals)

        # Set yWriter notes.

        if character.notes:
            self.lines.append(f'\n{self.characterNotesHeading}')
            self.lines.append(character.notes)