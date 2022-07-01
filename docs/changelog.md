[Project home page](index) > Changelog

------------------------------------------------------------------------

## Changelog

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

