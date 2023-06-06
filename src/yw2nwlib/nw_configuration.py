"""Provide a configuration class for reading and writing INI files.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.config.configuration import Configuration
from configparser import ConfigParser
import ast


class NwConfiguration(Configuration):
    """Read/write the program configuration.

    Public methods:
        read(iniFile) -- read a configuration file.
    
    Special version for configuration files that contain literal Python tuples. 
    """

    def read(self, iniFile):
        """Read a configuration file.
        
        Positional arguments:
            iniFile -- str: path configuration file path.
            
        Settings and options that can not be read in, remain unchanged.
        Overrides the superclass, adding list support. 
        """
        config = ConfigParser()
        config.read(iniFile)
        if config.has_section(self._sLabel):
            section = config[self._sLabel]
            for setting in self.settings:
                fallback = self.settings[setting]
                entry = section.get(setting, fallback)

                # convert lists.
                if isinstance(entry, str) and entry.startswith('('):
                    try:
                        entry = ast.literal_eval(entry)
                    except:
                        entry = fallback
                self.settings[setting] = entry
        if config.has_section(self._oLabel):
            section = config[self._oLabel]
            for option in self.options:
                fallback = self.options[option]
                self.options[option] = section.getboolean(option, fallback)
