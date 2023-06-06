""" Python unit tests for the yw2nw project.

Test suite for yw2nw.py.

For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import unittest
from shutil import copyfile, rmtree, copytree
import re
import yw2nw_

# Test environment

# The paths are relative to the "test" directory,
# where this script is placed and executed

TEST_PATH = f'{os.getcwd()}/../test'
TEST_DATA_PATH = f'{TEST_PATH}/data/'
TEST_EXEC_PATH = f'{TEST_PATH}/yw7/'

# To be placed in TEST_DATA_PATH:

# Test data
YW7_GENERATED = 'generated.yw7'
YW7_EDITED = 'edited.yw7'
NW_NORMAL = 'normal.nw'
NW_EDITED = 'edited.nw'
PROJECT = 'Sample Project'


def read_file(inputFile):
    try:
        with open(inputFile, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        # HTML files exported by a word processor may be ANSI encoded.
        with open(inputFile, 'r') as f:
            return f.read()


def adjust_timestamp(text):
    return re.sub('timeStamp=".*?"', 'timeStamp="2023-06-06 22:10:14"', text)


def remove_all_testfiles():
    try:
        os.remove(f'{TEST_EXEC_PATH}{PROJECT}.yw7')
    except:
        pass
    try:
        os.remove(f'{TEST_EXEC_PATH}{PROJECT}.yw7.bak')
    except:
        pass
    try:
        rmtree(f'{TEST_EXEC_PATH}{PROJECT}.nw')
    except:
        pass


class NormalOperation(unittest.TestCase):
    """Test case: Normal operation."""

    def setUp(self):
        try:
            os.mkdir(TEST_EXEC_PATH)
        except:
            pass
        remove_all_testfiles()

    def test_nw_to_yw7(self):
        copytree(f'{TEST_DATA_PATH}{NW_NORMAL}',
                 f'{TEST_EXEC_PATH}{PROJECT}.nw')
        os.chdir(TEST_EXEC_PATH)
        yw2nw_.run(f'{TEST_EXEC_PATH}{PROJECT}.nw/nwProject.nwx', doubleLinebreaks=True)
        self.assertEqual(read_file(f'{TEST_EXEC_PATH}{PROJECT}.yw7'),
                         read_file(f'{TEST_DATA_PATH}{YW7_GENERATED}'))

    def test_yw7_to_nw(self):
        copyfile(f'{TEST_DATA_PATH}{YW7_EDITED}', f'{TEST_EXEC_PATH}{PROJECT}.yw7')
        os.chdir(TEST_EXEC_PATH)
        yw2nw_.run(f'{TEST_EXEC_PATH}{PROJECT}.yw7', doubleLinebreaks=True)
        self.assertEqual(adjust_timestamp(read_file(f'{TEST_EXEC_PATH}{PROJECT}.nw/nwProject.nwx')),
                                            read_file(f'{TEST_DATA_PATH}{NW_EDITED}/nwProject.nwx'))
        contentFiles = os.listdir(f'{TEST_EXEC_PATH}{PROJECT}.nw/content')
        for contentFile in contentFiles:
            self.assertEqual(read_file(f'{TEST_EXEC_PATH}{PROJECT}.nw/content/{contentFile}'), read_file(
                                        f'{TEST_DATA_PATH}{NW_EDITED}/content/{contentFile}'))

    def tearDown(self):
        remove_all_testfiles()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
