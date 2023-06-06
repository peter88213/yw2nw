"""Provide a class for novelWriter character file representation.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.pywriter_globals import *
from pywriter.model.character import Character
from yw2nwlib.nwd_file import NwdFile


class NwdCharacterFile(NwdFile):
    """novelWriter character file representation.
    
    Public methods:
        read() -- read a content file.
        add_element(crId) -- add a character to the file content.
    """

    def __init__(self, prj, nwItem):
        """Define instance variables.
        
        Positional arguments:
            prj -- NwxFile instance: the novelWriter project represenation.
            nwItem -- NwItem instance associated with the .nwd file.        
        
        Required keyword arguments from prj:
            major_character_status -- tuple of str: novelWriter status meaning "Major" character importance in yWriter.
            character_notes_heading -- str: heading for novelWriter text that is converted to yWriter character notes.
            character_goals_heading -- str: heading for novelWriter text that is converted to yWriter character goals.
            character_bio_heading -- str: heading for novelWriter text that is converted to yWriter character bio.
            ywriter_aka_keyword -- str: keyword for 'aka' pseudo tag in novelWriter, signifying an alternative name.
            ywriter_tag_keyword -- str: keyword for 'tag' pseudo tag in novelWriter, signifying a yWriter tag.
            Extends the superclass constructor.
        """
        super().__init__(prj, nwItem)

        # Customizable Character importance.
        self._majorImportance = prj.kwargs['major_character_status']

        # Headings that divide the character sheet into sections.
        self._characterNotesHeading = prj.kwargs['character_notes_heading']
        self._characterGoalsHeading = prj.kwargs['character_goals_heading']
        self._characterBioHeading = prj.kwargs['character_bio_heading']

        # Customizable tags for characters and locations.
        self._ywAkaKeyword = f'%{prj.kwargs["ywriter_aka_keyword"]}: '
        self._ywTagKeyword = f'%{prj.kwargs["ywriter_tag_keyword"]}: '

    def read(self):
        """Read a content file.
        
        Return a message beginning with the ERROR constant in case of error.
        Extends the superclass method.
        """
        super().read()
        self._prj.crCount += 1
        crId = str(self._prj.crCount)
        self._prj.novel.characters[crId] = Character()
        self._prj.novel.characters[crId].fullName = self._nwItem.nwName
        self._prj.novel.characters[crId].title = self._nwItem.nwName
        desc = []
        bio = []
        goals = []
        notes = []
        section = 'desc'
        for line in self._lines:
            if not line:
                continue

            elif line.startswith('%%'):
                continue

            elif line.startswith('#'):
                section = 'desc'
                if line.startswith(self._characterBioHeading):
                    section = 'bio'
                elif line.startswith(self._characterGoalsHeading):
                    section = 'goals'
                elif line.startswith(self._characterNotesHeading):
                    section = 'notes'
            elif line.startswith('@'):
                if line.startswith('@tag'):
                    self._prj.novel.characters[crId].title = line.split(':')[1].strip().replace('_', ' ')
            elif line.startswith('%'):
                if line.startswith(self._ywAkaKeyword):
                    self._prj.novel.characters[crId].aka = line.split(':')[1].strip()
                elif line.startswith(self._ywTagKeyword):
                    if self._prj.novel.characters[crId].tags is None:
                        self._prj.novel.characters[crId].tags = []
                    self._prj.novel.characters[crId].tags.append(line.split(':')[1].strip())
            elif section == 'desc':
                desc.append(line)
            elif section == 'bio':
                bio.append(line)
            elif section == 'goals':
                goals.append(line)
            elif section == 'notes':
                notes.append(line)
        self._prj.novel.characters[crId].desc = '\n'.join(desc)
        self._prj.novel.characters[crId].bio = '\n'.join(bio)
        self._prj.novel.characters[crId].goals = '\n'.join(goals)
        self._prj.novel.characters[crId].notes = '\n'.join(notes)
        if self._nwItem.nwImportance in self._majorImportance:
            self._prj.novel.characters[crId].isMajor = True
        else:
            self._prj.novel.characters[crId].isMajor = False
        self._prj.novel.srtCharacters.append(crId)
        return 'Character data read in.'

    def add_character(self, crId):
        """Add a character to the file content.
        
        Positional arguments:
            crId -- str: character ID.
        """
        character = self._prj.novel.characters[crId]

        # Set Heading.
        if character.fullName:
            title = character.fullName
        else:
            title = character.title
        self._lines.append(f'# {title}\n')

        # Set tag.
        self._lines.append(f'@tag: {character.title.replace(" ", "_")}')

        # Set yWriter AKA.
        if character.aka:
            self._lines.append(self._ywAkaKeyword + character.aka)

        # Set yWriter tags.
        if character.tags is not None:
            for tag in character.tags:
                self._lines.append(self._ywTagKeyword + tag)

        # Set yWriter description.
        if character.desc:
            self._lines.append(f'\n{character.desc}')

        # Set yWriter bio.
        if character.bio:
            self._lines.append(f'\n{self._characterBioHeading}')
            self._lines.append(character.bio)

        # Set yWriter goals.
        if character.goals:
            self._lines.append(f'\n{self._characterGoalsHeading}')
            self._lines.append(character.goals)

        # Set yWriter notes.
        if character.notes:
            self._lines.append(f'\n{self._characterNotesHeading}')
            self._lines.append(character.notes)
