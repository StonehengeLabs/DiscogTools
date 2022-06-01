# pip install mutagen
from mutagen.id3 import ID3
from mutagen.id3 import TPE1
from mutagen.id3 import COMM
from mutagen.id3 import TALB
from mutagen.id3 import TCON
from mutagen.id3 import TIT2
from mutagen.id3 import TPUB
from mutagen.id3 import TYER

def tags_set_all(copy, track, tags):
    tags['TPE1'] = TPE1(encoding=3, text=track.artist)
    tags['TALB'] = TALB(encoding=3, text=copy.release.title_with_catno(copy))
    tags['TCON'] = TCON(encoding=3, text=copy.release.genres[0])
    tags['TIT2'] = TIT2(encoding=3, text=track.title)
    tags['TPUB'] = TPUB(encoding=3, text=copy.release.label)

    if not copy.release.year == None:
        tags['TYER'] = TYER(encoding=3, text=copy.release.year)

    tags_set_comments(copy, track, tags)

    tags_normalize_serato(tags)

def tags_set_comments(copy, track, tags):
    tags.delall('COMM')
    tags['COMM'] = COMM(encoding=3, lang='eng', text=track.id3_comment(copy))
    # tags['COMM'] = COMM(encoding=3, lang='eng', text='HOHOHOHO')

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
