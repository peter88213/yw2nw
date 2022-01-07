"""Provide a class for novelWriter scene file representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywnw.nwd_file import NwdFile


class NwdSceneFile(NwdFile):
    """novelWriter scene file representation.
    """

    def write(self, scId):
        """Write a content file. 
        Return a message beginning with SUCCESS or ERROR.
        """
        scene = self.prj.scenes[scId]

        if scene.appendToPrev:
            self.lines.append('#### ' + scene.title + '\n')

        else:
            self.lines.append('### ' + scene.title + '\n')

        # Set synopsis.

        if scene.desc:
            self.lines.append('% Synopsis: ' + scene.desc + '\n')

        # Set scene content.

        text = scene.sceneContent

        if text:
            self.lines.append(text)

        return NwdFile.write(self)
