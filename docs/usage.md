[Project homepage](https://peter88213.github.io/yw2nw)

---

The yw2nw Python script converts yWriter 7 projects to new novelWriter projects and vice versa.

## Instructions for use

### Intended usage

After installation, create a shortcut on the desktop. 
- If you drag a novelWriter project file named *nwProject.nwx* onto it and drop it, a new yWriter project is created one directory level below. Existing files are saved with the file extension *.bak*. 
- If you drag a yWriter project file with extension *.yw7* and drop it on the icon, a new novelWriter project is generated in a directory named after the yWriter file. Existing novel writer project directories will be renamed as a whole and get the extension *.bak*. 
If there is already such a directory, a new, numbered backup directory is created with the  extension *.bkxxxx*

### Command line usage

Alternatively, you can

- launch the program on the command line passing the yWriter/novelWriter project file as an argument, or
- launch the program via a batch file.

usage: `yw2nw.py [-h] [--silent] Sourcefile`

#### positional arguments:

`Sourcefile` 

The path of the .nwx or .yw7 file. 

#### optional arguments:

`-h, --help` 

show this help message and exit

`-d, --double_linebreaks` 

paragraph breaks are represented by double line breaks in novelWriter

`--silent` 

suppress error messages and the request to confirm overwriting

## Conventions and known limitations

### Mapping

| Topic                      | yWriter                                        | novelWriter                               |
| -------------------------- | ---------------------------------------------- | ----------------------------------------- |
| **Novel 1st level**        |                                                |                                           |
| "Part" (novelWriter)       | Chapter marked as beginning of a new section   | Text with a first level heading           |
| Part synopsis              | Chapter description                            | Text prefixed by "*% synopsis :*"         |
| **Novel 2nd level**        |                                                |                                           |
| Chapter                    | Chapter                                        | Text with a second level heading          |
| Chapter synopsis           | Chapter description                            | Text prefixed by *% synopsis :*           |
| **Novel 3rd level**        |                                                |                                           |
| Scene                      | Scene                                          | Text with a third level heading           |
| Scene synopsis             | Scene description                              | Text prefixed by *% synopsis :*           |
| **Novel 4th level**        |                                                |                                           |
| "Section" (novelWriter)    | Scene appended to the previous without divider | Text with a fourth level heading          |
| Section synopsis           | Scene description                              | Text prefixed by *% synopsis :*           |
| **State of completion**    | Scene status                                   | Status (scenes/sections only)             |
| **Characters**             |                                                |                                           |
| Character				     | Character                                      | Character (tagged)                        |
| Character full name        | Character full name                            | First level heading in the character file |
| Character short name       | Character name                                 | Text prefixed by *@tag :*                 |
| Character alternative name | Character aka                                  | Text prefixed by *%aka :*                 |
| Character	biography    	 | Character bio                                  | Text with a "## Bio" heading              |
| Character	goals            | Character goals                                | Text with a "## Goals" heading            |
| Point of view	reference    | Scene viewpoint character                      | Text in scene prefixed by *@pov :*        |
| Character reference 	     | Scene character                                | Text in scene prefixed by *@character *   |
| **World building**         |                                                |                                           |
| Location				     | Location                                       | Location (tagged)                         |
| Location alternative name  | Location aka                                   | Text prefixed by *%aka :*                 |
| Location description       | Location description                           | Text body below the first heading         |
| Location reference         | Scene location entry                           | Text prefixed by *@loc*                   |

### Novel structure

-  Body text after a 1st or 2nd level heading in *novelWriter* is converted into a auto-named scene in *yWriter*.


### Metadata

- *yWriter*'s scene date/time/duration are lost when converting to *novelWriter*. 
- *yWriter*'s scene action/reaction flags are lost when converting to *novelWriter*. 
- *yWriter*'s scene goal/conflict/outcome are lost when converting to *novelWriter*. 
- *yWriter*'s scene importance flags (*Plot/Subplot*) are lost when converting to *novelWriter*. 
- *yWriter*'s scene ratings are lost when converting to *novelWriter*. 

### Text formatting

- Bold, italics, and strikethrough are supported. Other highlighting such as underline are lost.
- Paragraph alignment such as centering or right-aligning is not supported. *novelWriter* 
  markup is treated like regular text when converting to *yWriter*. *yWriter* markup is lost.
- Inline RTF, TEX and HTML markup in yWriter scenes is treated like regular text when converting to *novelWriter*.
- *yWriter*'s global and text variables are not expanded when converting to *novelWriter*.
- *novelWriter*'s auto replacement (if any) is not supported.

### Comments

- Inline comments within the *yWriter* scene text are treated like regular text when converting to *novelWriter*.
- Commented-out lines in the *novelWriter* text body (except ones that begin with a supported keyword)
  are lost when converting to *yWriter*.
  
#### Tags

- *novelWriter*'s **pov**, **char**, **location** tags are supported. Others are lost. 
- Only scene tags are converted from *novelWriter* to *yWriter*. Part and chapter tags are lost.
- *yWriter* scene/character/location tags are converted to *novelWriter* comments with customizable 
  keywords. They can be re-converted back to *yWriter*.


## Custom configuration

You can override the default settings by providing a configuration file. Be always aware that faulty entries may cause program errors or unreadable projects. 

The global configuration file is placed in the configuration directory in your user profile. It is applied to any project. Its entries override yw2nw's built-in constants. This is the path:
`c:\Users\<user name>\.pywriter\yw2nw\config\yw2nw.ini`
  
The setup script installs a sample configuration file containing yw2nw's default values. You can modify or delete it. 

### How to provide/modify a configuration file

The yw2nw distribution comes with a sample configuration file located in the `sample` subfolder. It contains yw2nw's default settings and options. This file is also automatically copied to the global configuration folder during installation. You best make a copy and edit it.

- The SETTINGS section comprises the program "constants". If you change them, the program might behave differently than described in the documentation. So only touch them if you are clear about the consequences.
- The OPTIONS section comprises options for regular program execution. 
- Comment lines begin with a `#` number sign. In the example, they refer to the code line immediately above.

This is the configuration explained: 

```
[SETTINGS]
outline_status = ['Outline', 'New', 'Notes']

# This novelWriter status are converted to yWriter "Outline"
# scene status.

draft_status = ['Draft', 'Started', '1st Draft']

# This novelWriter status are converted to yWriter "Draft"
# scene status.

first_edit_status = ['1st Edit', '2nd Draft']

# This novelWriter status are converted to yWriter "1st Edit"
# scene status.

second_edit_status = ['2nd Edit', '3rd Draft']

# This novelWriter status are converted to yWriter "2nd Edit"
# scene status.

done_status = ['Done', 'Finished']

# This novelWriter status are converted to yWriter "Done"
# scene status.

scene_status = ['None', 'Outline', 'Draft', '1st Edit', '2nd Edit', 'Done']

# This status are used when creating a new novelWriter project from
# yWriter.
# You can rename them, but the number of list entries must not change.

major_character_status = ['Major', 'Main']

# This novelWriter status are converted to yWriter "Major" character
# importance.

character_notes_heading = ## Notes

# Heading for novelWriter character text that is converted to yWriter
# character notes.

character_goals_heading = ## Goals

# Heading for novelWriter character text that is converted to yWriter
# character goals.

character_bio_heading = ## Bio

# Heading for novelWriter character text that is converted to yWriter
# character bio.

ywriter_aka_keyword = aka

# Keyword for 'aka' pseudo tag in novelWriter character text, signifying
# an alternative name. 
# Usage: "%aka: <character's alternative name>"
# One aka per character.

ywriter_tag_keyword = tag

# Keyword for 'tag' pseudo tag in novelWriter character text, signifying
# a yWriter tag. 
# Usage: "%tag: <character, location, or scene tag>"
# If there are multiple tags assigned, put each one on its own line.

[OPTIONS]
double_linebreaks = Yes

# "Yes" -- In novelWriter, paragraphs are separated by double line breaks,
#          as is supported by novelWriter's document export.
# "No"  -- In novelWriter, paragraphs are separated by single line breaks,
#          as is common in prose texts.
# Note: "No" is overridden by the "-d" command line parameter.


```

## Markdown reference

By default, *yw2nw* converts a Markdown subset according to the following specificatiions:

### Paragraphs

By default, double line breaks are considered paragraph breaks, as is the Markdown standard
supported by *novelWriter*'s document export. In this case, single blank lines in yWriter
scenes are Markdown-encoded by three blank lines.

You can change the converter's behavior by changing the *double_linebreaks* setting in
the configuration file to "No". Then single line breaks are considered paragraph breaks,
as is common in prose texts.

NOTE: *double_linebreaks = No* is not compliant with novelWriter's standard (version 1.6alpha),
so you better don't use this option if you want to use *novelWriter*'s built-in document export. 

Standard Markdown behavior kan be enforced by setting the command line parameter *-d*. 

### Headings

#### Level 1 heading used for parts (chapters marked as beginning of a new section in yWriter)
`# One hash character at the start of the line`

#### Level 2 heading used for chapters
`## Two hash characters at the start of the line`

### Emphasis

#### Italic 
`_single underscores_`

**Note** : A `_` surrounded with spaces will be treated as a literal underscore.

#### Bold 
`**double asterisks**`

#### Strikethrough 
`~~double swung dashes~~`



## Installation path

The setup script installs *yw2nw.py* in the user profile. This is the installation path on Windows: 

`c:\Users\<user name>\.pywriter\yw2nw`


