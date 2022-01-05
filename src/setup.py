#!/usr/bin/env python3
"""Install the aeon2yw script. 

Version @release

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import stat
from shutil import copyfile
from pathlib import Path
from string import Template

try:
    from tkinter import *
    from tkinter import messagebox

except ModuleNotFoundError:
    print('The tkinter module is missing. Please install the tk support package for your python3 version.')
    sys.exit(1)


APPNAME = 'aeon2yw'

VERSION = ' @release'
APP = APPNAME + '.pyw'
INI_FILE = APPNAME + '.ini'
INI_PATH = '/config/'
SAMPLE_PATH = 'sample/'
SUCCESS_MESSAGE = '''

$Appname is installed here:

$Apppath'''

SHORTCUT_MESSAGE = '''
Now you might want to create a shortcut on your desktop.  

On Windows, open the installation folder, hold down the Alt key on your keyboard, 
and then drag and drop $Appname.pyw to your desktop.

On Linux, create a launcher on your desktop. With xfce for instance, the launcher's command may look like this:
python3 '$Apppath' %F
'''


root = Tk()
processInfo = Label(root, text='')
message = []


def output(text):
    message.append(text)
    processInfo.config(text=('\n').join(message))


def open_folder(installDir):
    """Open an installation folder window in the file manager.
    """

    try:
        os.startfile(os.path.normpath(installDir))
        # Windows
    except:

        try:
            os.system('xdg-open "%s"' % os.path.normpath(installDir))
            # Linux
        except:

            try:
                os.system('open "%s"' % os.path.normpath(installDir))
                # Mac

            except:
                pass


def install(pywriterPath):
    """Install the script."""

    # Create a general PyWriter installation directory, if necessary.

    os.makedirs(pywriterPath, exist_ok=True)
    installDir = pywriterPath + APPNAME
    cnfDir = installDir + INI_PATH

    if os.path.isfile(installDir + '/' + APP):
        simpleUpdate = True

    else:
        simpleUpdate = False

    try:
        # Move an existing installation to the new place, if necessary.

        oldInstDir = os.getenv('APPDATA').replace('\\', '/') + '/pyWriter/' + APPNAME
        os.replace(oldInstDir, installDir)
        output('Moving "' + oldInstDir + '" to "' + installDir + '"')

    except:
        pass

    os.makedirs(cnfDir, exist_ok=True)

    # Delete the old version, but retain configuration, if any.

    with os.scandir(installDir) as files:

        for file in files:

            if not 'config' in file.name:
                os.remove(file)
                output('Removing "' + file.name + '"')

    # Install the new version.

    copyfile(APP, installDir + '/' + APP)
    output('Copying "' + APP + '"')

    # Make the script executable under Linux.

    st = os.stat(installDir + '/' + APP)
    os.chmod(installDir + '/' + APP, st.st_mode | stat.S_IEXEC)

    # Install a configuration file, if needed.

    try:
        if not os.path.isfile(cnfDir + INI_FILE):
            copyfile(SAMPLE_PATH + INI_FILE, cnfDir + INI_FILE)
            output('Copying "' + INI_FILE + '"')

        else:
            output('Keeping "' + INI_FILE + '"')

    except:
        pass

    # Install the Aeon2 sample template, if needed.

    try:
        aeon2dir = os.getenv('LOCALAPPDATA').replace('\\', '/') + '/Scribble Code/Aeon Timeline 2/CustomTemplates/'
        sampleTemplate = 'yWriter.xml'

        if not os.path.isfile(aeon2dir + sampleTemplate):
            copyfile(SAMPLE_PATH + sampleTemplate, aeon2dir + sampleTemplate)
            output('Copying "' + sampleTemplate + '"')

        else:
            if messagebox.askyesno('Aeon Timeline 2 "yWriter" template', 'Update "' + aeon2dir + sampleTemplate + '"?'):
                copyfile(SAMPLE_PATH + sampleTemplate, aeon2dir + sampleTemplate)
                output('Updating "' + sampleTemplate + '"')

            else:
                output('Keeping "' + sampleTemplate + '"')

    except:
        pass

    # Display a success message.

    mapping = {'Appname': APPNAME, 'Apppath': installDir + '/' + APP}

    output(Template(SUCCESS_MESSAGE).safe_substitute(mapping))

    # Ask for shortcut creation.

    if not simpleUpdate:
        output(Template(SHORTCUT_MESSAGE).safe_substitute(mapping))


if __name__ == '__main__':

    # Open a tk window.

    root.geometry("800x600")
    root.title('Install ' + APPNAME + VERSION)
    header = Label(root, text='')
    header.pack(padx=5, pady=5)

    # Prepare the messaging area.

    processInfo.pack(padx=5, pady=5)

    # Run the installation.

    pywriterPath = str(Path.home()).replace('\\', '/') + '/.pywriter/'
    install(pywriterPath)

    # Show options: open installation folders or quit.

    root.openButton = Button(text="Open installation folder", command=lambda: open_folder(pywriterPath + APPNAME))
    root.openButton.config(height=1, width=30)
    root.openButton.pack(padx=5, pady=5)
    root.quitButton = Button(text="Quit", command=quit)
    root.quitButton.config(height=1, width=30)
    root.quitButton.pack(padx=5, pady=5)
    root.mainloop()
