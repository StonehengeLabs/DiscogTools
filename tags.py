
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
