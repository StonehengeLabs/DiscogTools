from normalize import *
from copy import Copy

class Track:

    def __init__(self, release, artist, position, title):
        self.release = release
        if artist:
            self.artist = normalize_artist(artist)
        else:
            self.artist = release.artist
        self.position = position
        self.title = normalize_title(title)

    def mp3_filename(self, copy):
        catext = ''
        if not copy.copynote == None:
            catext = ' ' + copy.copynote
        return f'{self.release.catno}{catext} {self.position} - {self.artist} - {self.title}.mp3'
