from normalize import *
from releasecopy import Copy
class Release:

    def __init__(self, id, label, catno, year, artist, title, genres):
        self.id, self.label, self.catno, self.year, self.artist, self.title, self.genres = id, normalize_label(label), normalize_catno(catno, id), year, normalize_artist(artist), normalize_title(title), genres
        self.tracks = []
    
    def add_track(self, track):
        self.tracks.append(track)

    def formatted(self):
        return f'{self.id} {self.catno} "{self.artist}" - "{self.title}"'

    def title_with_catno(self, appendix = ""):
        title_and_catno = ''
        if len(self.title) == 0:
            title_and_catno = self.catno
        else:
            title_and_catno = self.title
        if len(self.catno) > 0:
            title_and_catno = title_and_catno + " (" + self.catno + ")"
        if len(title_and_catno) == 0:
            title_and_catno = "Unknown"
        if len(appendix) > 0:
            title_and_catno = title_and_catno + ", " + appendix
        return title_and_catno

    def matches_title_with_catno(self, candidate):
        title_and_catno = self.title_with_catno()
        return candidate.startswith(title_and_catno)

    def img_filename(self, copy, ext = 'jpg'):
        catext = ''
        if not copy.copynote == None:
            catext = ' ' + copy.copynote
        basename = NormalizeFileBaseName(f'{self.id}{catext} {self.title} ({self.catno}) - {self.artist}')
        return f'{basename}.{ext}'
