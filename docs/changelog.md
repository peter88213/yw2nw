[Project home page](index) > Changelog

------------------------------------------------------------------------

## Changelog

### v1.0.1

- Remove language markup, if any.

Based on PyWriter v12.12.0

### v1.0.0

- Notes are generally assumed "active".
- Library update.

Based on PyWriter v12.12.0

### v0.10.4

- Make it run with old Windows versions.

Based on PyWriter v6.0.2

### v0.10.3

- Fix a bug where conversion fails if the novelWriter project has no author.
- Fix a bug where conversion fails if status or importance attributes are missing.
- Replace linebreaks with tabs when converting chapter descriptions to synopses.
- Make "Outline" the default status for new scenes.

Based on Pywriter v6.0.0

### v0.10.2

- Replace linebreaks with tabs when converting scene descriptions to synopses.

Based on Pywriter v6.0.0

### v0.10.1

- Modify "shebang" line to make the script run with Python 3.11 under Windows.

Based on Pywriter v6.0.0

### v0.10.0

- Full file format 1.5 support (read and write). 
- Drop file format 1.3 support. 

Based on Pywriter v6.0.0

### v0.9.0 Update to file format 1.5

- Add file format 1.5 support (read only). 
- Drop file format 1.4 support. 

Based on Pywriter v6.0.0

### v0.8.6

- Fix Chapter "Type" and "ChapterType" inconsistencies when writing .yw7 files.
- Fix a bug in the pywriter Novel class: Initialize "public" instance variables the correct way.
- The pywriter library is prepared for internationalization with GNU gettext.

Based on Pywriter v6.0.0

### v0.8.5 Update setup script

- Change the working dir to the script dir on startup in order to avoid "file not found" error.

Based on PyWriter v5.18.0

### v0.8.4 Improved setup

- Catch exceptions in the setup script.

Based on PyWriter v5.18.0

### v0.8.3 Improved word counting

- Fix word counting considering ellipses.

Based on PyWriter v5.12.4

### v0.8.2 Beta release

- Fix word counting considering comments, hyphens, and dashes.

Based on PyWriter v5.12.3

### v0.8.1 Beta release

Optimize the code.
When reading the NWX file, process the flat XML structure
without evaluating the items' child/parent relations.

This works under the following assumptions:
- The NOVEL items are arranged in the correct order.
- ARCHIVE and TRASH sections are located at the end. 

Based on PyWriter v5.0.3

### v0.8.0 Beta release

- Change the configuration: replace lists by tuples.
- Fix a bug in the setup script where the sample configuration file is not installed.
- Update the documentation.
- Improve code quality by refactoring and formatting.

Based on PyWriter v5.0.3

### v0.6.0 beta release

- Add support of novelWriter file format version 1.4.
- Fix a bug where a wrong backup file name is displayed when overwriting yw7.
- Fix a bug where "To do" chapters cause an exception.
- Rework the command line messages. 
- Refactor the code.

Based on PyWriter v5.0.0

### v0.4.4 alpha release

- Refactor the code.

Based on PyWriter v3.32.3

### v0.4.3 alpha release

- Fix a bug where lists in the configuration file are processed the wrong way.

Based on PyWriter v3.32.2

### v0.4.2 alpha release

- Fix a bug where an exception is thrown if a project has no objects.
- Convert unused scenes to not exported and vice versa.

Based on PyWriter v3.32.1

### v0.4.1 alpha release

Fix misplaced formatting tags before converting them to Markdown.

Based on PyWriter v3.32.0.

### v0.4.0 alpha release

Support yWriter items as NovelWriter objects.

Based on PyWriter v3.32.0.

### v0.2.0 First public alpha release

Based on PyWriter v3.32.0.

