import os

from collection import Collection
from djcase import DjCase

from env import *
from tags import *

# pip install mutagen
from mutagen.id3 import ID3

collection = Collection(file_path_collection_json)
djcase = DjCase(dir_path_vinyl)

for copy in collection.copies:
    # print(copy.formatted())

    complete = True
    for track in copy.recorded_tracks:
        # print(track.mp3_filename(copy))
        if not os.path.exists(os.path.join(dir_path_vinyl, track.mp3_filename(copy))):
            complete = False
    
    #if not complete:
    #    print('')
    #    print(copy.formatted())
    #    print("   => Skipped due to structural mismatch.")
    #else:
    if complete:
        skip_copy, fix_all_copy = False, False
        for track in copy.recorded_tracks:
            if not skip_copy:
                mp3_file_path = os.path.join(dir_path_vinyl, track.mp3_filename(copy))
                tags = ID3()
                tags.load(mp3_file_path, translate = False)
                correct = tags_verify_comments(copy, track, tags)
                if not correct:
                    comment_tags = tags.getall('COMM')
                    comment_tag_text = track.id3_comment(copy)

                    command = 'f'
                    if not fix_all_copy:
                        print('')
                        print(copy.formatted())
                        for comment_tag in comment_tags:
                            print("      - {0:<15}".format(comment_tag.desc) + comment_tag.text[0])
                        print("      - {0:<15}".format('Expected') + comment_tag_text)
                        command = input('\ns to skip whole copy; f to fix this track; enter to fix all copy\'s tracks: ')
                    if command == 's':
                        skip_copy = True
                    elif command == '':
                        fix_all_copy = True
                        command = 'f'
                    if command == 'f':
                        tags_set_comments(copy, track, tags)
                        tags_normalize_serato(tags)
                        tags.save()
                        print(track.mp3_filename(copy) + ": comments")
