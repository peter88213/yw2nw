#!/usr/bin/env python3
"""Helper file for yw2nw test.

Create config file.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import sys
import os
from pywriter.config.configuration import Configuration
from yw2nw_ import SETTINGS
from yw2nw_ import OPTIONS
from yw2nw_ import APPNAME


def run(iniFile):
    iniDir = os.path.dirname(iniFile)
    if not os.path.isdir(iniDir):
        os.makedirs(iniDir)
    configuration = Configuration(SETTINGS, OPTIONS)
    configuration.write(iniFile)
    print(f'{iniFile} written.')


if __name__ == '__main__':
    try:
        iniFile = sys.argv[1]
    except:
        iniFile = f'./{APPNAME}.ini'
    run(iniFile)
