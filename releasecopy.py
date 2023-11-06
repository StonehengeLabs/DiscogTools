import re

class Copy:

    def __init__(self, release, fullnote, copynote, folder):
        self.release, self.fullnote, self.copynote, self.folder = release, fullnote, copynote, folder

        self.recorded_tracks = []
        self.unrecorded_tracks = []
        for track in release.tracks:
            if fullnote:
                if re.match('.*\{-' + re.escape(track.position) + '\}.*', fullnote, re.MULTILINE | re.DOTALL):
                    self.unrecorded_tracks.append(track)
                else:
                    self.recorded_tracks.append(track)
            else:
                self.recorded_tracks.append(track)

        self.copynote_string_component = '' # self.copynote with a leading space if there is a copynote (convenient for string composition).
        if self.copynote:
            self.copynote_string_component = ' ' + self.copynote

    def rar_filename(self):
        return f'{self.release.id} {self.release.title_with_catno(self)} - {self.release.artist}.rar'

    def formatted(self):
        return f'{self.release.formatted()}\n   {self.copynote} / {self.folder} / {self.fullnote}'

    def is_recorded(self, position):
        have = False
        for track in self.recorded_tracks:
            if track.position == position:
                have = True
                break
        return have

    def unrecorded_positions(self):
        positions = []
        for track in self.unrecorded_tracks:
            positions.append(track.position)
        return positions
        