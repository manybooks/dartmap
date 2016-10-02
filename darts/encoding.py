import codecs
import sys

def sfnc_none(name):
    if name.lower() == "none":
        return codecs.lookup("utf-8")

def sfnc_Windows31J(name):
    if name.lower() == "windows-31j":
        return codecs.lookup("cp932")

UNKNOWN_ENCODING = [sfnc_Windows31J, sfnc_none]

def search_functions():
    """returns the list of CodecInfo object that searchs unknown encoding"""
    return UNKNOWN_ENCODING
