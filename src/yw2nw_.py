#!/usr/bin/env python3
"""Convert yWriter to novelWriter

Version @release
Requires Python 3.7 or above

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import argparse
from pathlib import Path

from pywriter.ui.ui import Ui
from pywriter.ui.ui_cmd import UiCmd
from pywriter.config.configuration import Configuration

from pywnw.nw_converter import NwConverter

SUFFIX = ''
APPNAME = 'yw2nw'

SETTINGS = dict(
    # part_heading_prefix='#',
    # chapter_heading_prefix='##',
    # scene_heading_prefix='###',
    # section_heading_prefix='####',
    outline_status=['New', 'Notes'],
    draft_status=['Started', '1st Draft'],
    first_edit_status=['2nd Draft'],
    second_edit_status=['3rd Draft'],
    done_status=['Finished'],
    major_character_status=['Major', 'Main'],
    character_notes_heading='## Notes',
    character_goals_heading='## Goals',
    character_bio_heading='## Bio',
    world_element_aka_tag='AKA',
    world_element_tag_tag='tag',
)

OPTIONS = dict(
)


def run(sourcePath, silentMode=True, installDir=''):

    if silentMode:
        ui = Ui('')

    else:
        ui = UiCmd('Synchronize Aeon Timeline 2 and yWriter @release')

    #--- Try to get persistent configuration data

    sourceDir = os.path.dirname(sourcePath)

    if sourceDir == '':
        sourceDir = './'

    else:
        sourceDir += '/'

    iniFileName = APPNAME + '.ini'
    iniFiles = [installDir + iniFileName, sourceDir + iniFileName]

    configuration = Configuration(SETTINGS, OPTIONS)

    for iniFile in iniFiles:
        configuration.read(iniFile)

    kwargs = {'suffix': SUFFIX}
    kwargs.update(configuration.settings)
    kwargs.update(configuration.options)

    converter = NwConverter()
    converter.ui = ui
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='yWriter import and export for novelWriter',
        epilog='')
    parser.add_argument('sourcePath',
                        metavar='Sourcefile',
                        help='The path of the nwx or yw7 file.')

    parser.add_argument('--silent',
                        action="store_true",
                        help='suppress error messages and the request to confirm overwriting')
    args = parser.parse_args()

    try:
        installDir = str(Path.home()).replace('\\', '/') + '/.pywriter/' + APPNAME + '/config/'

    except:
        installDir = ''

    run(args.sourcePath, args.silent, installDir)
