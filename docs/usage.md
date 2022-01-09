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

- launch the program on the command line passing the yWriter/Timeline project file as an argument, or
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

### Text formatting

- Bold, italics, and strikethrough are supported. Other highlighting such as underline are lost.
- Paragraph alignment such as centering or right-aligning is not supported. *novelWriter* 
  markup is treated like regular text when converting to *yWriter*. *yWriter* markup is lost.
- Inline RTF, TEX and HTML markup in yWriter scenes is treated like regular text when converting to *novelWriter*.

### Comments

- Inline comments within the *yWriter* scene text are treated like regular text when converting to *novelWriter*.
- Commented-out lines in the *novelWriter* text body (except ones that begin with a supported keyword)
  are lost when converting to *yWriter*.
  
### Metadata

#### Tags

- *novelWriter*'s **pov**, **char**, **location** tags are supported. Others are lost. 
- Only scene tags are converted from *novelWriter* to *yWriter. Part and chapter tags are lost.
- yWriter scene/character/location tags are converted to *novelWriter* comments with customizable 
  keywords. They can be re-converted back to *yWriter*.


## Custom configuration

You can override the default settings by providing a configuration file. Be always aware that faulty entries may cause program errors or unreadable projects. 

### Global configuration

An optional global configuration file can be placed in the configuration directory in your user profile. It is applied to any project. Its entries override yw2nw's built-in constants. This is the path:
`c:\Users\<user name>\.pywriter\yw2nw\config\yw2nw.ini`
  
The setup script installs a sample configuration file containing yw2nw's default values. You can modify or delete it. 

### Local project configuration

An optional project configuration file named `yw2nw.ini` can be placed in your project directory, i.e. the folder containing your yWriter or novelWriter project files. It is only applied to this project. Its entries override yw2nw's built-in constants as well as the global configuration, if any.

### How to provide/modify a configuration file

The yw2nw distribution comes with a sample configuration file located in the `sample` subfolder. It contains yw2nw's default settings and options. This file is also automatically copied to the global configuration folder during installation. You best make a copy and edit it.

- The SETTINGS section comprises the program "constants". If you change them, the program might behave differently than described in the documentation. So only touch them if you are clear about the consequences.
- The OPTIONS section comprises options for regular program execution. 
- Comment lines begin with a `#` number sign. In the example, they refer to the code line immediately above.

This is the configuration explained: 

```
[SETTINGS]
outline_status = ['Outline', 'New', 'Notes']

# This novelWriter status are converted to yWriter "Outline" scene status.

draft_status = ['Draft', 'Started', '1st Draft']

# This novelWriter status are converted to yWriter "Draft" scene status.

first_edit_status = ['1st Edit', '2nd Draft']

# This novelWriter status are converted to yWriter "1st Edit" scene status.

second_edit_status = ['2nd Edit', '3rd Draft']

# This novelWriter status are converted to yWriter "2nd Edit" scene status.

done_status = ['Done', 'Finished']

# This novelWriter status are converted to yWriter "Done" scene status.

scene_status = ['None', 'Outline', 'Draft', '1st Edit', '2nd Edit', 'Done']

# This status are used when creating a new novelWriter project from yWriter.
# You can rename them, but the number of list entries must not change.

major_character_status = ['Major', 'Main']

# This novelWriter status are converted to yWriter "Major" character importance.

character_notes_heading = ## Notes

# Heading for novelWriter character text that is converted to yWriter character notes.

character_goals_heading = ## Goals

# Heading for novelWriter character text that is converted to yWriter character goals.

character_bio_heading = ## Bio

# Heading for novelWriter character text that is converted to yWriter character bio.

ywriter_aka_keyword = aka

# Keyword for 'aka' pseudo tag in novelWriter character text, signifying an alternative name. 
# Usage: "%aka: <character's alternative name>"
# One aka per character.

ywriter_tag_keyword = tag

# Keyword for 'tag' pseudo tag in novelWriter character text, signifying a yWriter tag. 
# Usage: "%tag: <character, location, or scene tag>"
# If there are multiple tags assigned, put each one on its own line.

[OPTIONS]
double_linebreaks = No

# "Yes" -- In novelWriter, paragraphs are separated by a double line break,
#          as intended by novelWriter's author.
# "No"  -- In novelWriter, paragraphs are separated by a simple line break.
# Note: This is overridden by the "-d" command line parameter.
```

## Markdown reference

By default, *yw2nw* converts a Markdown subset according to the following specificatiions:

### Paragraphs

By default, single line breaks are considered paragraph breaks, as is common in prose texts.

NOTE: This is not compliant with novelWriter's standard, so you better use the *-d* option 
if you want to use *novelWriter*'s built-in document export:

You can change the converter's behavior by either setting the *double_linebreaks* option in
the configuration file, or by setting the command line parameter *-d*. Then double line 
breaks are considered paragraph breaks, as is the Markdown standard supported by *novelWriter*. 
In this case, single blank lines in yWriter scenes are Markdown-encoded by three blank lines.

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



## Installation path

The setup script installs *yw2nw.py* in the user profile. This is the installation path on Windows: 

`c:\Users\<user name>\.pywriter\yw-timeline`


