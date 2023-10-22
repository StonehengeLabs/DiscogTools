
import json

from release import Release
from track import Track
from releasecopy import Copy

class Collection:

    def __init__(self, json_file):
        self.releases = {}
        self.copies = []
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            for json_copy in json_data['releases']:
                release_id = json_copy['id']
                if not release_id in self.releases:
                    self.register_release(json_copy)
                release = self.releases[release_id] # There now.
                copy = Copy(release, json_copy.get('fullnote', None), json_copy.get('copynote', None), json_copy['folder'])
                self.copies.append(copy)

    def register_release(self, json_copy):
        release = Release(json_copy['id'], json_copy['label'], json_copy['catno'], json_copy.get('year', None), json_copy['artist'], json_copy['title'], json_copy['genres'])
        self.releases[release.id] = release

        for json_track in json_copy['tracks']:
            release.add_track(Track(release, json_track.get('artist', None), json_track['position'], json_track['title']))

    def copies_by_release_id(self, release_id, copynote = None):
        matches = []
        for copy in self.copies:
            if copy.release.id == release_id:
                if copynote:
                    if copynote == copy.copynote:
                        matches.append(copy)
                else:
                    matches.append(copy)
        return matches
