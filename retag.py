import sys
import re
import os
import shutil

from collection import Collection
from djcase import DjCase
from mp3file import Mp3File

# pip install mutagen
from mutagen.id3 import ID3

file_path_collection_json = 'C:/Portables/DiscogParser/collection.json'
dir_path_vinyl = 'C:/Stefan/Static/DjCase/vinyl'
dir_path_output = 'C:/Stefan/Dynamic/Scratch/Mp3Factory/retagged'

collection = Collection(file_path_collection_json)
djcase = DjCase(dir_path_vinyl)

if len(sys.argv) < 2:
    print("Usage: retag.py <release-id> [<copynote>]")
    exit(1)

release_id = int(sys.argv[1])
copies = collection.copies_by_release_id(release_id)

if len(copies) > 1:
    if len(sys.argv) < 3:
        for copy in copies:
            print("Match: " + copy.formatted())
        print("\nMore than one copy of this release; need to specify a copynote.")
        print("Usage: retag.py <release-id> [<copynote>]")
        exit(1)
    copynote = sys.argv[2]
    copies = collection.copies_by_release_id(release_id, copynote)

if not len(copies) == 1:
    print('Copy matching failed.')
    exit(1)

copy = copies[0]
print(copy.formatted())
print('\n--- Tracks should be: ---')
for i in range(0, len(copy.recorded_tracks)):
    print(f'({i}) {copy.recorded_tracks[i].mp3_filename(copy)}')
unrecorded_positions = copy.unrecorded_positions()
if len(unrecorded_positions) > 0:
    print('(-) Unrecorded positions: ' + ', '.join(unrecorded_positions))

print('\n--- Closest matches: ---')
track_filenames_current = []
for track in copy.recorded_tracks:
    track_filenames_current.append(djcase.get_most_similar_filename(track.mp3_filename(copy)))

while True:
    for i in range(0, len(track_filenames_current)):
        print(f'({i}) {track_filenames_current[i]}')

    command = input('\nEnter r to retag; track number to move a track to top; any other input to abort: ')
    if re.match('\d+', command):
        print('\n--- Reordered matches: ---')
        track_index = int(command) - 1
        if track_index < 1 or track_index >= len(track_filenames_current):
            continue
        track_filenames_current = [ track_filenames_current[track_index] ] + track_filenames_current[:track_index] + track_filenames_current[track_index + 1:]
        continue

    if not command == 'r':
        print("Aborted.")
        exit(0)

    break

for i in range(0, len(copy.recorded_tracks)):
    filename_current, filename_corrected = track_filenames_current[i], copy.recorded_tracks[i].mp3_filename(copy)
    filepath_corrected = os.path.join(dir_path_output, filename_corrected)
    shutil.copy(os.path.join(dir_path_vinyl, filename_current), filepath_corrected)

    id3 = ID3()
    id3.load(filepath_corrected, translate = False)
    print('--------------')
    print(id3.pprint())
    print('--------------')
    print(id3['TPE1'])
    
    # https://mutagen.readthedocs.io/en/latest/api/id3.html#mutagen.id3.ID3Tags


    # file = Mp3File(os.path.join(dir_path_vinyl, track))

