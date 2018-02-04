import os

def getOppositeOSDirectorySep():
    if os.sep == '/':
        return '\\'
    else:
        return '/'