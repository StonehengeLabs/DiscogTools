from normalize import *
from copy import Copy
class Release:

    def __init__(self, id, label, catno, year, artist, title, genres):
        self.id, self.label, self.catno, self.year, self.artist, self.title, self.genres = id, normalize_label(label), normalize_catno(catno), year, normalize_artist(artist), normalize_title(title), genres
        self.tracks = []
    
    def add_track(self, track):
        self.tracks.append(track)

    def formatted(self):
        return f'{self.id} {self.catno} "{self.artist}" - "{self.title}"'

    def title_with_catno(self, copy):
        title_and_catno = ''
        if len(copy.release.title) == 0:
            title_and_catno = copy.release.catno
        else:
            title_and_catno = copy.release.title
        if len(copy.release.catno) > 0:
            title_and_catno = title_and_catno + " (" + copy.release.catno + ")"
        if len (title_and_catno) == 0:
            title_and_catno = "Unknown"
        return title_and_catno

    def img_filename(self, copy, ext = 'jpg'):
        catext = ''
        if not copy.copynote == None:
            catext = ' ' + copy.copynote
        basename = NormalizeFileBaseName(f'{self.id}{catext} {self.title} ({self.catno}) - {self.artist}')
        return f'{basename}.{ext}'
