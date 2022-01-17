"""Provide a class to manage novelWriter handles.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from hashlib import pbkdf2_hmac


class Handles():
    """Hold a list of novelWriter compatible handles.
    The only purpose of this list is to use unique handles.
    Therefore, it is not intended to delete members.
    """
    HANDLE_CHARS = list('abcdef0123456789')
    SIZE = 13

    def __init__(self):
        self._handles = []

    def has_member(self, handle):
        """Return True if handle is in the list.
        """
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
        """Create a handle derived from text and add it to the list.
        Return the handle.
        Use a non-random algorithm in order to faciliate testing.
        """

        def create_handle(text, salt):
            """Return a handle for novelWriter.
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
