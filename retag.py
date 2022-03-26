import sys
import re
import os
import shutil
import glob

from collection import Collection
from djcase import DjCase
from mp3file import Mp3File

# pip install mutagen
from mutagen.id3 import ID3
from mutagen.id3 import TPE1
from mutagen.id3 import COMM
from mutagen.id3 import TALB
from mutagen.id3 import TCON
from mutagen.id3 import TIT2
from mutagen.id3 import TPUB
from mutagen.id3 import TYER

file_path_collection_json = 'C:/Portables/DiscogParser/collection.json'
dir_path_vinyl = 'C:/Stefan/Static/DjCase/vinyl'
dir_path_output = 'C:/Stefan/Dynamic/Scratch/Mp3Factory/retagged'
dir_path_work = 'C:/Stefan/Dynamic/Scratch/Mp3Factory'

collection = Collection(file_path_collection_json)
djcase = DjCase(dir_path_vinyl)

if len(sys.argv) < 2:
    print("Usage: retag.py <release-id>")
    exit(1)

release_id = int(sys.argv[1])
copies = collection.copies_by_release_id(release_id)

if len(copies) > 1:
    print('\n--- More than one copy of this release: ---')
    copynotes = []
    for i in range(0, len(copies)):
        print(f'({i + 1}) {copies[i].copynote}')
        copynotes.append(copies[i].copynote)
    command = input('\nSelect a copy: ')
    copy_index = None
    if re.match('\d+', command):
        i = int(command) - 1
        if i >= 0 and i < len(copies):
            copy_index = i
    if copy_index == None:
        print("Invalid selection.")
        exit(1)
    copies = collection.copies_by_release_id(release_id, copynotes[copy_index])

if not len(copies) == 1:
    print('Copy matching failed.')
    exit(1)

copy = copies[0]
print(copy.formatted())
print('\n--- Tracks should be: ---')
for i in range(0, len(copy.recorded_tracks)):
    print(f'({i + 1}) {copy.recorded_tracks[i].mp3_filename(copy)}')
unrecorded_positions = copy.unrecorded_positions()
if len(unrecorded_positions) > 0:
    print('(-) Unrecorded positions: ' + ', '.join(unrecorded_positions))

print('\n--- Closest matches: ---')
track_filenames_current = []
for track in copy.recorded_tracks:
    track_filenames_current.append(djcase.get_most_similar_filename(track.mp3_filename(copy)))

renamed, remapped = False, False
while True:
    for i in range(0, len(track_filenames_current)):
        print(f'({i + 1}) {track_filenames_current[i]}')

    command = input('\nEnter r to retag; track number to move a track to top; any other input to abort: ')
    if re.match('\d+', command):
        print('\n--- Reordered matches: ---')
        track_index = int(command) - 1
        if track_index < 1 or track_index >= len(track_filenames_current):
            continue
        track_filenames_current = [ track_filenames_current[track_index] ] + track_filenames_current[:track_index] + track_filenames_current[track_index + 1:]
        remapped = True
        continue

    if not command == 'r':
        print("Aborted.")
        exit(0)

    break

for i in range(0, len(copy.recorded_tracks)):
    track = copy.recorded_tracks[i]
    filename_current, filename_corrected = track_filenames_current[i], track.mp3_filename(copy)
    filepath_corrected = os.path.join(dir_path_output, filename_corrected)
    print('    ' + filename_current + '\n -> ' + filename_corrected)
    shutil.copy(os.path.join(dir_path_vinyl, filename_current), filepath_corrected)

    if not filename_current == filename_corrected:
        renamed = True

    # https://mutagen.readthedocs.io/en/latest/api/id3.html#mutagen.id3.ID3Tags
    tags = ID3()
    tags.load(filepath_corrected, translate = False)
    #print('--------------')
    #print(tags.pprint())
    #print('--------------')

    tags['TPE1'] = TPE1(encoding=3, text=track.artist)
    tags['TALB'] = TALB(encoding=3, text=copy.release.title_with_catno(copy))
    tags['TCON'] = TCON(encoding=3, text=copy.release.genres[0])
    tags['TIT2'] = TIT2(encoding=3, text=track.title)
    tags['TPUB'] = TPUB(encoding=3, text=copy.release.label)
    tags['TYER'] = TYER(encoding=3, text=copy.release.year)

    tags.delall('COMM')
    tags['COMM'] = COMM(encoding=3, lang='eng', text=track.id3_comment(copy))

    playcounts = tags.getall('TXXX')
    for p in playcounts:
        if p.desc == 'SERATO_PLAYCOUNT':
            p.text = u'0'

    tags.save()

if renamed or remapped:
    # Now we must adjust the .wav file names as well. Problem is that we know only the new name of the image name, not the old one.
    # Therefore, we guess the old image name by using the release ID of the current (= old) file names.
    src_filenames_current, src_filenames_corrected = [], []
    for i in range(0, len(copy.recorded_tracks)):
        track = copy.recorded_tracks[i]
        src_filenames_current  .append(track_filenames_current[i][:-4] + ".wav")
        src_filenames_corrected.append(track.wav_filename(copy))
    for i in range(0, len(copy.recorded_tracks) + 1): # Will add image file in first iteration (need 1st file present to guess image file name)
        source = os.path.join(dir_path_work, src_filenames_current[i])
        while not os.path.exists(source):
            command = input(f"\nNeed to rename:\n    '{src_filenames_current[i]}'\nPlease get it and confirm...")
        print(f'   {src_filenames_current[i]}\n')
        print(f'-> {src_filenames_corrected[i]}\n')
        shutil.move(source, os.path.join(dir_path_work, 'source', src_filenames_corrected[i]))
        if i == 0: # Now that the source archive has probably been extracted and the sources are available, we can search & schedule the image file as well...
            refs = re.match('(\d+)\s.+', src_filenames_current[0])
            old_release_id = refs.group(1) # The old release ID is in fact likely to be the same as the new one, but you never know.
            matches = glob.glob(os.path.join(dir_path_work, f'{old_release_id} *.jpg'))
            print(matches)
            if not len(matches) == 1:
                print('Unplausible number of source image file matches: ')
                print(matches)
                exit(1)
            src_filenames_current  .append(os.path.basename(matches[0]))
            src_filenames_corrected.append(copy.release.img_filename(copy))

print(f"\nOutput folder is 'file:///{dir_path_output}'.")

