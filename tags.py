# pip install mutagen
from mutagen.id3 import ID3
from mutagen.id3 import TPE1
from mutagen.id3 import COMM
from mutagen.id3 import TALB
from mutagen.id3 import TCON
from mutagen.id3 import TIT2
from mutagen.id3 import TPUB
from mutagen.id3 import TDRC

def tags_load(filepath):
    tags = ID3() # https://mutagen.readthedocs.io/en/latest/api/id3.html#mutagen.id3.ID3Tags
    tags.load(filepath, translate = True, v2_version = 4, load_v1 = False)
    return tags

def tags_save(tags):

    # If we just load and save tags, the id3v1 comment is lost for whatever reason.
    # Workaround: get comment text and reassign it to tags. This seems to make mutagen
    # keep the comment in the id3v1 as well.
    comment_tags = tags.getall('COMM')
    text = None

    for comment_tag in comment_tags:
        if len(comment_tag.text) == 1:
            if not comment_tag.desc == 'ID3v1 Comment':
                text = comment_tag.text[0]

    tags.delall('COMM')
    tags['COMM'] = COMM(encoding=3, lang='eng', text=text)

    tags.save()

def tags_set_all(copy, track, tags):
    tags['TPE1'] = TPE1(encoding=3, text=track.artist)
    tags['TCON'] = TCON(encoding=3, text=copy.release.genres[0])
    tags['TIT2'] = TIT2(encoding=3, text=track.title_with_position)
    tags['TPUB'] = TPUB(encoding=3, text=copy.release.label)

    if not copy.release.year == None:
        tags['TDRC'] = TDRC(encoding=3, text=copy.release.year)

    tags_set_album(copy, track, tags)
    tags_set_comments(copy, track, tags)

    tags_normalize_serato(tags)

def tags_get_album(tags):
    return tags['TALB'].text[0]

def tags_verify(copy, track, tags):
    errors = []

    generalMismatches = []
    tagged_artist = tags['TPE1'].text[0]
    tagged_album  = tags['TALB'].text[0]
    tagged_genres = tags['TCON'].text[0]
    tagged_title  = tags['TIT2'].text[0]
    tagged_label  = tags['TPUB'].text[0]
    if not tagged_artist == track.artist:
        generalMismatches.append(f'artist: (old) {tagged_artist} => (new) {track.artist}')
    if not tagged_album == copy.title_with_catno_and_short_folder():
        generalMismatches.append(f'album: (old) {tagged_album} => (new) {copy.title_with_catno_and_short_folder()}')
    if not tagged_genres == copy.release.genres[0]:
        generalMismatches.append(f'genre: (old) {tagged_genres} => (new) {copy.release.genres[0]}')
    if not tagged_title == track.title_with_position:
        generalMismatches.append(f'title: (old) {tagged_title} => (new) {track.title_with_position}')
    if not tagged_label == copy.release.label:
        generalMismatches.append(f'label: (old) {tagged_label} => (new) {copy.release.label}')

    if len(generalMismatches) > 0:
        mlist = ', '.join(generalMismatches)
        errors.append(f'   Track {track.position} needs retag:')
        for m in generalMismatches:
            errors.append(f'      {m}')
    else:
        if not tags_verify_comments(copy, track, tags):
            errors.append(f'   Track {track.position} needs reloc.')

    return errors

def tags_verify_comments(copy, track, tags):
    comment_tags = tags.getall('COMM')
    comment_tag_text = track.id3_comment(copy)

    correct = True
    for comment_tag in comment_tags:
        if len(comment_tag.text) != 1:
            correct = False
        else:
            if comment_tag.desc == 'ID3v1 Comment': # ID3 V1 comment is only 28 bytes long.
                if comment_tag.text[0][0:27] != comment_tag_text[0:27]:
                    correct = False
            else:
                if comment_tag.text[0] != comment_tag_text:
                    correct = False

    return correct

def tags_set_comments(copy, track, tags):
    tags.delall('COMM')
    tags['COMM'] = COMM(encoding=3, lang='eng', text=track.id3_comment(copy))

def tags_set_album(copy, track, tags):
    tags['TALB'] = TALB(encoding=3, text=copy.title_with_catno_and_short_folder())

def tags_normalize_serato(tags):
    tags_normalize_playcount(tags)
    tags_normalize_beatgrid(tags)

def tags_normalize_playcount(tags):
    reset = False
    playcounts = tags.getall('TXXX')
    for p in playcounts:
        if p.desc == 'SERATO_PLAYCOUNT':
            if not p.text == [ u'0' ]:
                p.text = [ u'0' ]
                reset = True
    
    return reset

def tags_normalize_beatgrid(tags):
    reset = False
    geobs = tags.getall('GEOB')
    for g in geobs:
        if g.desc == 'Serato BeatGrid':
            arr = bytearray(g.data)
            if arr[-1] != 0:
                arr = arr[:-1] # Last byte of beatgrid seems to be random, see https://github.com/Holzhaus/serato-tags/blob/master/docs/serato_beatgrid.md ...
                arr.append(0) # ... so replace it with zero to normalize.
                g.data = bytes(arr)
                reset = True

    return reset
