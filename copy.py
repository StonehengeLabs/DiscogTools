import re

class Copy:

    def __init__(self, release, fullnote, copynote, folder):
        self.release, self.fullnote, self.copynote, self.folder = release, fullnote, copynote, folder

        self.recorded_tracks = []
        self.unrecorded_tracks = []
        for track in release.tracks:
            if fullnote:
                if re.match('.*\{-' + track.position + '\}.*', fullnote):
                    self.unrecorded_tracks.append(track)
                else:
                    self.recorded_tracks.append(track)
            else:
                self.recorded_tracks.append(track)

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
        