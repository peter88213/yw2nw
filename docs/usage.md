[Project homepage](https://peter88213.github.io/yw2nw)

---

The yw2nw Python script converts yWriter 7 projects to new novelWriter projects and vice versa.

This script is meant to be launched from the command line. However, 
if you prefer to use the mouse, you can create a link on your 
desktop, and launch yw2nw by dragging the source file and dropping 
it to the link icon. For optional arguments, edit the configuration file.


## Usage
usage: `yw2nw.py [-h] [--silent] Sourcefile`

#### positional arguments:

`Sourcefile` 

The path of the .nwx or .yw7 file for the conversion. 

- If it's a yWriter project file with extension '.yw7', 
a new novelWriter project will be created in a directory named after the yWriter file.
- Existing novel writer project directories will be renamed as a whole and get the extension '.bak'. 
If there is already such a directory, a new, numbered backup directory is created with the  extension '.bkxxxx'
- If it's a novelWriter project named 'nwProject.nwx', 
a new yWriter 7 project will be created one directory level below. 
- Existing yWriter projects are backed up with  the extension '.bak' before overwritten.


#### optional arguments:

`-h, --help` show this help message and exit

`--silent` suppress error messages and the request to confirm overwriting

