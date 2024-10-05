import os

from collection import Collection
from djcase import DjCase

from env import *
from tags import *

# pip install mutagen
from mutagen.id3 import ID3

collection = Collection(file_path_collection_json)
djcase = DjCase(dir_path_vinyl)

fix_all_global = False

for copy in collection.copies:
    # print(copy.formatted())

    process = True
    tags_per_position = dict() # Optimization (import tags only once)
    for track in copy.recorded_tracks:
        # print(track.mp3_filename(copy))
        mp3_file_path = os.path.join(dir_path_vinyl, track.mp3_filename(copy))
        if not os.path.exists(mp3_file_path):
            process = False
        else:
            tags = tags_load(mp3_file_path)
            tags_per_position[track.position] = tags
            if not copy.release.matches_title_with_catno(tags_get_album(tags)): # WAV sources need to be renamed.
                process = False

    if not process:
        print('')
        print(copy.formatted())
        print("   => Skipped due to structural mismatch.")
    else:
        skip_copy, fix_all_copy = False, fix_all_global
        for track in copy.recorded_tracks:
            if not skip_copy:
                mp3_file_path = os.path.join(dir_path_vinyl, track.mp3_filename(copy))
                tags = tags_per_position[track.position]
                errors = tags_verify(copy, track, tags)
                if len(errors) > 0:
                    command = 'f'
                    if not fix_all_copy:
                        print('')
                        print(copy.formatted())
                        print('')
                        for error in errors:
                            print(error)
                        command = input('\ns to skip whole copy; f to fix this track; enter to fix all copy\'s tracks, e to fix everything: ')
                    if command == 's':
                        skip_copy = True
                    if command == 'e':
                        fix_all_global = True
                        command = ''
                    if command == '':
                        fix_all_copy = True
                        command = 'f'
                    if command == 'f':
                        tags_set_all(copy, track, tags)
                        tags_normalize_serato(tags)
                        tags_save(tags)
                        print(track.mp3_filename(copy) + ": retagged")
