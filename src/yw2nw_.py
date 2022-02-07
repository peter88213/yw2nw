#!/usr/bin/env python3
"""Convert yWriter to novelWriter

Version @release
Requires Python 3.6+
Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import argparse
from pathlib import Path

from pywriter.ui.ui import Ui
from pywriter.ui.ui_cmd import UiCmd
from pywnw.nw_configuration import NwConfiguration

from pywnw.nw_converter import NwConverter

SUFFIX = ''
APPNAME = 'yw2nw'

SETTINGS = dict(
    outline_status=['Outline', 'New', 'Notes'],
    draft_status=['Draft', 'Started', '1st Draft'],
    first_edit_status=['1st Edit', '2nd Draft'],
    second_edit_status=['2nd Edit', '3rd Draft'],
    done_status=['Done', 'Finished'],
    scene_status=['None', 'Outline', 'Draft', '1st Edit', '2nd Edit', 'Done'],
    major_character_status=['Major', 'Main'],
    character_notes_heading='## Notes',
    character_goals_heading='## Goals',
    character_bio_heading='## Bio',
    ywriter_aka_keyword='aka',
    ywriter_tag_keyword='tag',
    # part_heading_prefix='#',
    # chapter_heading_prefix='##',
    # scene_heading_prefix='###',
    # section_heading_prefix='####',
)

OPTIONS = dict(
    double_linebreaks=True
)


def run(sourcePath, doubleLinebreaks=False, silentMode=True, installDir=''):

    if silentMode:
        ui = Ui('')

    else:
        ui = UiCmd('Converter between yWriter and novelWriter @release')

    #--- Try to get persistent configuration data

    sourceDir = os.path.dirname(sourcePath)

    if not sourceDir:
        sourceDir = './'

    else:
        sourceDir = f'{sourceDir}/'

    iniFileName = f'{APPNAME}.ini'
    iniFiles = [f'{installDir}{iniFileName}']

    configuration = NwConfiguration(SETTINGS, OPTIONS)

    for iniFile in iniFiles:
        configuration.read(iniFile)

    kwargs = {'suffix': SUFFIX}
    kwargs.update(configuration.settings)
    kwargs.update(configuration.options)

    # Override the paragraph break convention by command line parameter.

    if doubleLinebreaks:
        kwargs['double_linebreaks'] = True

    converter = NwConverter()
    converter.ui = ui
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Converter between yWriter and novelWriter',
        epilog='')
    parser.add_argument('sourcePath',
                        metavar='Sourcefile',
                        help='The path of the .nwx or .yw7 file.')

    parser.add_argument('-d', '--double_linebreaks',
                        action="store_true",
                        help='paragraph breaks are represented by double line breaks in novelWriter')

    parser.add_argument('--silent',
                        action="store_true",
                        help='suppress error messages and the request to confirm overwriting')
    args = parser.parse_args()

    try:
        homeDir = str(Path.home()).replace('\\', '/')
        installDir = f'{homeDir}/.pywriter/{APPNAME}/config/'

    except:
        installDir = ''

    run(args.sourcePath, args.double_linebreaks, args.silent, installDir)
