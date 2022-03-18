from normalize import *

class Release:

    def __init__(self, id, label, catno, year, artist, title, genres):
        self.id, self.label, self.catno, self.year, self.artist, self.title, self.genres = id, normalize_label(label), normalize_catno(catno), year, normalize_artist(artist), normalize_title(title), genres
        self.tracks = []
    
    def add_track(self, track):
        self.tracks.append(track)

    def formatted(self):
        return f'{self.id} {self.catno} "{self.artist}" - "{self.title}"'
