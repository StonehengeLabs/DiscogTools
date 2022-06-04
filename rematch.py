import sys
import re
import os
import shutil

from collection import Collection
from djcase import DjCase
from mp3file import Mp3File
from filematcher import FileMatcher

from env import *
from tags import *

# pip install mutagen
from mutagen.id3 import ID3

def rematch(release_id):

    collection = Collection(file_path_collection_json)
    djcase = DjCase(dir_path_vinyl)

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

    unrecorded_positions = copy.unrecorded_positions()
    if len(unrecorded_positions) > 0:
        print('Unrecorded positions: ' + ', '.join(unrecorded_positions))

    mp3_names_to_be = []
    for track in copy.recorded_tracks:
        mp3_names_to_be.append(track.mp3_filename(copy))
    matcher = FileMatcher(copy.release.id, "MP3", mp3_names_to_be, dir_path_vinyl, '*.mp3')
    renamed, track_filenames_current = matcher.select()

    for i in range(0, len(copy.recorded_tracks)):
        track = copy.recorded_tracks[i]
        filename_current, filename_corrected = track_filenames_current[i], track.mp3_filename(copy)
        filepath_corrected = os.path.join(dir_path_output_mp3, filename_corrected)
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

        tags_set_all(copy, track, tags)
        tags.save()

    if renamed:
        # If at least one file was renamed, we remove all old MP3 files from the vinyl path.
        for filename_current in track_filenames_current:
            os.remove(os.path.join(dir_path_vinyl, filename_current))

        # Now we must adjust the .jpg and .wav file names as well.
        print('\nSources as well...')
        src_filenames_current, src_filenames_corrected = [], []
        release_id = copy.release.id # Release ID is considered to be unchanged.

        for track in copy.recorded_tracks:
            src_filenames_corrected.append(track.wav_filename(copy))
        src_filenames_corrected.append(copy.release.img_filename(copy))

        matcher = FileMatcher(copy.release.id, "Source", src_filenames_corrected, dir_path_work, '*.*')
        renamed, src_filenames_current = matcher.select()

        for i in range(0, len(src_filenames_current)):
            print('    ' + src_filenames_current[i] + '\n -> ' + src_filenames_corrected[i])
            shutil.move(os.path.join(dir_path_work, src_filenames_current[i]), os.path.join(dir_path_output_wav, src_filenames_corrected[i]))

    # print(f"\nOutput folder is 'file:///{dir_path_output_mp3}'.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: rematch.py <release-id>")
        exit(1)

    release_id = int(sys.argv[1])
    rematch(release_id)
