import os
import sys

from env import *
from tags import *
from filematcher import *

from collection import Collection
from djcase import DjCase

# pip install mutagen
from mutagen.id3 import ID3

sys.stdout.reconfigure(encoding='utf-8')

collection = Collection(file_path_collection_json)
djcase = DjCase(dir_path_vinyl)

mp3_filenames = djcase.mp3_filenames()

for copy in collection.copies:
    # print(copy.formatted())

    if not (copy.folder == "Unrecorded" or (copy.folder == "Uncategorized" and copy.fullnote == "waschen") or (copy.folder == "Missing" and copy.fullnote == "Unrecorded")):

        errors = []

        for track in copy.recorded_tracks:

            mp3_filename = track.mp3_filename(copy)
            if mp3_filename in mp3_filenames:
                mp3_filenames.remove(mp3_filename)
                # print(track.mp3_filename(copy))
                mp3_file_path = os.path.join(dir_path_vinyl, mp3_filename)
                tags = tags_load(mp3_file_path)
                errors = errors + tags_verify(copy, track, tags)

            else:
                candidate = FileMatcher.get_most_similar_filename(mp3_filename, mp3_filenames)
                errors.append(f'   Missing:   {mp3_filename}')
                errors.append(f'   Candidate: {candidate}')

        if len(errors) > 0:
            print(f'\n[https://www.discogs.com/release/{copy.release.id}] has issues:')
            for error in errors:
                print(error)
