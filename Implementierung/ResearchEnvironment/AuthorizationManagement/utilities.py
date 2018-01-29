import os

def getOppositeOSDirectorySep():
    if os.sep is '/':
        return '\\'
    else:
        return '/'