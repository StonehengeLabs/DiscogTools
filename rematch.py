import sys
import re
import os
import shutil
from subprocess import Popen, PIPE

from collection import Collection
from filematcher import FileMatcher

from env import *
from tags import *

# pip install mutagen
from mutagen.id3 import ID3

def rematch(release_id):

    collection = Collection(file_path_collection_json)

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
        tags = tags_load(filepath_corrected)
        #print('--------------')
        #print(tags.pprint())
        #print('--------------')

        if not copy.release.matches_title_with_catno(tags_get_album(tags)):
            renamed = True # If the album title has changed, we must rename files in the sources as well - note that the mp3s are NOT renamed in this case, therefore extra check here.
                           # Album appendix (short_folder) is not relevant.

        tags_set_all(copy, track, tags)
        tags_save(tags)

    # We remove all old MP3 files from the vinyl path, even if no file was renamed. This is for uniorm handling of retagged files.
    for filename_current in track_filenames_current:
        os.remove(os.path.join(dir_path_vinyl, filename_current))

    if renamed:
        # If at least one file was renamed, we must adjust the .jpg and .wav file names as well.
        print('\nSources as well...')

        matcher = FileMatcher(copy.release.id, "Archive", [ copy.rar_filename() ], dir_path_source_archives, '*.rar', True)
        renamed, rar_filenames = matcher.select()
        if len(rar_filenames) == 1:
            try:
                print(f'Moving {rar_filenames[0]} from {dir_path_source_archives}...')
                shutil.move(os.path.join(dir_path_source_archives, rar_filenames[0]), os.path.join(dir_path_work, rar_filenames[0]))
                if os.path.isfile(unrar_exe_path):
                    print(f'Locally unpacking {rar_filenames[0]}...')
                    process = Popen( [ unrar_exe_path, 'x', rar_filenames[0] ], cwd = dir_path_work, stdout=PIPE, stderr=PIPE)
                    process.communicate()
                    if process.returncode == 0:
                        os.rename(os.path.join(dir_path_work, rar_filenames[0]), os.path.join(dir_path_work, 'TRASH_' + rar_filenames[0]))
                    else:
                        print('Error unpacking archive.')
                else:
                    print('UnRAR executable not found; please extract manually.')
            except:
                print(f'Failed to move archive.')

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
