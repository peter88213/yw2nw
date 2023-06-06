"""Helper module for removing PyWriter specific data.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import re

__all__ = ['reset_custom_variables']


def reset_custom_variables(prjFile):
    """Set custom keyword variables of a File instance to an empty string.
    
    Positional arguments:
        prjFile -- File instance to process.
    
    Thus the Yw7File.write() method will remove the associated custom fields
    from the .yw7 XML file. 
    Return True, if a keyword variable has changed (i.e information is lost).
    """
    hasChanged = False
    for field in prjFile.PRJ_KWVAR:
        if prjFile.novel.kwVar.get(field, None):
            prjFile.novel.kwVar[field] = ''
            hasChanged = True
    for chId in prjFile.novel.chapters:
        # Deliberatey not iterate srtChapters: make sure to get all chapters.
        for field in prjFile.CHP_KWVAR:
            if prjFile.novel.chapters[chId].kwVar.get(field, None):
                prjFile.novel.chapters[chId].kwVar[field] = ''
                hasChanged = True
    for scId in prjFile.novel.scenes:
        for field in prjFile.SCN_KWVAR:
            if prjFile.novel.scenes[scId].kwVar.get(field, None):
                prjFile.novel.scenes[scId].kwVar[field] = ''
                hasChanged = True
    for crId in prjFile.novel.characters:
        for field in prjFile.CRT_KWVAR:
            if prjFile.novel.characters[crId].kwVar.get(field, None):
                prjFile.novel.characters[crId].kwVar[field] = ''
                hasChanged = True
    for lcId in prjFile.novel.locations:
        for field in prjFile.LOC_KWVAR:
            if prjFile.novel.locations[lcId].kwVar.get(field, None):
                prjFile.novel.locations[lcId].kwVar[field] = ''
                hasChanged = True
    for itId in prjFile.novel.items:
        for field in prjFile.ITM_KWVAR:
            if prjFile.novel.items[itId].kwVar.get(field, None):
                prjFile.novel.items[itId].kwVar[field] = ''
                hasChanged = True
    for pnId in prjFile.novel.projectNotes:
        for field in prjFile.PNT_KWVAR:
            if prjFile.novel.projectnotes[pnId].kwVar.get(field, None):
                prjFile.novel.projectnotes[pnId].kwVar[field] = ''
                hasChanged = True
    return hasChanged


def remove_language_tags(novel):
    """Remove language tags from the document.
    
    Positional arguments:
        novel -- Novel instance to process.    
    
    Remove the language tags from the scene contents.
    Return True, if changes have been made to novel.
    """
    languageTag = re.compile('\[\/*?lang=.*?\]')
    hasChanged = False
    for scId in novel.scenes:
        text = novel.scenes[scId].sceneContent
        try:
            text = languageTag.sub('', text)
        except:
            pass
        else:
            if  novel.scenes[scId].sceneContent != text:
                novel.scenes[scId].sceneContent = text
                hasChanged = True
    return hasChanged

