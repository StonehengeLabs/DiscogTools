

# pip install mutagen
from mutagen.id3 import ID3


class Mp3File:

    def __init__(self, filename):
        self.tags = ID3()
        self.tags.load(filename, translate = False)
        print(self.tags.version)
        
