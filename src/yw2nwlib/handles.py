"""Provide a class to manage novelWriter handles.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from hashlib import pbkdf2_hmac


class Handles:
    """Hold a list of novelWriter compatible handles.
    
    The only purpose of this list is to use unique handles.
    Therefore, it is not intended to delete members.
    """
    HANDLE_CHARS = list('abcdef0123456789')
    SIZE = 13

    def __init__(self):
        """Initialize the list of handles."""
        self._handles = []

    def has_member(self, handle):
        """Return True if handle is in the list of handles."""
        return handle in self._handles

    def add_member(self, handle):
        """Add handle to the list, if unique and compliant.
        
        Return True on success.
        Return False if handle is not accepted for any reason.
        """
        if self.has_member(handle):
            return False

        if len(handle) != self.SIZE:
            return False

        for c in handle:
            if not c in self.HANDLE_CHARS:
                return False

        self._handles.append(handle)
        return True

    def create_member(self, text):
        """Create a handle derived from text and add it to the list of handles.

        Positional arguments:
            text -- string from which the handle is derived.
        
        Return the handle.
        Use a non-random algorithm in order to faciliate testing.
        If text is not unique, a "salt" is varied until a unique handle is achieved. 
        """

        def create_handle(text, salt):
            """Return a handle for novelWriter.
            
            Positional arguments:
                text -- string from which the handle is derived.
                salt -- additional string to make the handle unique. 
            """
            text = text.encode('utf-8')
            key = pbkdf2_hmac('sha1', text, bytes(salt), 1)
            keyInt = int.from_bytes(key, byteorder='big')
            handle = ''
            while len(handle) < self.SIZE and keyInt > 0:
                handle += self.HANDLE_CHARS[keyInt % len(self.HANDLE_CHARS)]
                keyInt //= len(self.HANDLE_CHARS)
            return handle

        i = 0
        handle = create_handle(text, i)
        while not self.add_member(handle):
            i += 1
            if i > 1000:
                raise ValueError('Unable to create a proper handle.')

            handle = create_handle(text, i)
        return(handle)
