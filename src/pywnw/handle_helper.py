"""Provide a file handle generator for novelWriter.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from hashlib import pbkdf2_hmac

handleChars = list('abcdef0123456789')


def get_handle(text, salt):
    """Return a handle for novelWriter.
    """
    text = text.encode('utf-8')
    size = 13
    key = pbkdf2_hmac('sha1', text, bytes(salt), 1)
    keyInt = int.from_bytes(key, byteorder='big')
    handle = ''

    while len(handle) < size and keyInt > 0:
        handle += handleChars[keyInt % len(handleChars)]
        keyInt //= len(handleChars)

    return handle
