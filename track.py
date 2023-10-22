from normalize import *
from releasecopy import Copy

class Track:

    def __init__(self, release, artist, position, title):
        self.release = release
        if artist:
            self.artist = normalize_artist(artist)
        else:
            self.artist = release.artist
        self.position = position
        self.title = normalize_title(title)

    def wav_filename(self, copy):
        catext = ''
        if not copy.copynote == None:
            catext = ' ' + copy.copynote
        basename = NormalizeFileBaseName(f'{self.release.id}{catext} {self.position} {self.release.title} ({self.release.catno}) - {self.artist} - {self.title}')
        return f'{basename}.wav'

    def mp3_filename(self, copy):
        catext = ''
        if not copy.copynote == None:
            catext = ' ' + copy.copynote
        basename = NormalizeFileBaseName(f'{self.release.catno}{catext} {self.position} - {self.artist} - {self.title}')
        return f'{basename}.mp3'

    def id3_comment(self, copy):
        trackComment = ""
        if not copy.folder == None:
            trackComment = copy.folder + ", "
        trackComment += f'{self.release.id}{copy.copynote_string_component}, {self.position}'
        return trackComment
