import os
import json
import hashlib

from djcase import DjCase

from env import *
from tags import *

def md5(fname): # https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

djcase = DjCase(dir_path_vinyl)

mp3states, mp3states_prev = dict(), dict()
if os.path.isfile(file_path_mp3states_json):
    with open(file_path_mp3states_json) as json_file:
        mp3states_prev = json.load(json_file)

for filepath in djcase.mp3_filepaths():

    operations = list()

    # Stage 1: add it if it is not registered...

    just_added = False
    if filepath in mp3states_prev:
        mp3states[filepath] = mp3states_prev[filepath]
    else:
        now_lastmod = os.path.getmtime(filepath)
        now_checksum = md5(filepath)
        mp3states[filepath] = { 'last_modified': now_lastmod, 'checksum_md5': now_checksum }
        operations.append('A')
        just_added = True

    # Stage 2: reset tags if applicable...

    now_lastmod = os.path.getmtime(filepath)
    sns_lastmod = mp3states[filepath]['last_modified']

    if just_added or (now_lastmod != sns_lastmod):
        tags = tags_load(filepath)
        mod = False
        if tags_normalize_playcount(tags):
            operations.append('C')
            mod = True
        if tags_normalize_beatgrid(tags):
            operations.append('G')
            mod = True
        if mod:
            tags_save(tags)

    # Stage 3: reset timestamp if applicable...

    now_lastmod = os.path.getmtime(filepath)
    sns_lastmod = mp3states[filepath]['last_modified']

    if now_lastmod != sns_lastmod:
        now_checksum = md5(filepath)
        sns_checksum = mp3states[filepath]['checksum_md5']

        if now_checksum == sns_checksum:
            os.utime(filepath, (sns_lastmod, sns_lastmod))
            operations.append('T')
        else:
            mp3states[filepath] = { 'last_modified': now_lastmod, 'checksum_md5': now_checksum }
            operations.append('U')

    # Output...
    if len(operations) > 0:
        operations_aligned = ''
        for op in ('A', 'G', 'C', 'U', 'T'):
            pos = op if op in operations else '-'
            operations_aligned = operations_aligned + pos
        print(f'{operations_aligned} {os.path.basename(filepath)}')

with open(file_path_mp3states_json, 'w') as json_file:
    json.dump(mp3states, json_file, indent=4, sort_keys=True)
