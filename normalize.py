import re 

def normalize_artist(artist):
   if artist:
      artist = re.sub('\s\(\d+\)', "", artist) # This removes discogs indices. May be subject to discussion.
      artist = artist.strip()
      artist = artist.replace(" / ", ", ")
      artist = artist.replace("ā", "a") # For Prānā - boundless EP. This is not in the Latin-1 space.
      artist = artist.replace("™", "(TM)") # For release 83942. This is not in the Latin-1 space.
      artist = artist.replace("–", "-") # For Sebasian Arnold's beeeah-music.
      artist = artist.replace("フォーテック", "Photek") # For release 309.
   return artist

def normalize_label(label):
   return normalize_artist(label) # Same rules, as it seems.

def normalize_title(title):
   title = title.replace("“", "") # For release 21001810.
   title = title.replace("”", "") # For release 21001810.
   title = title.replace(" / ", ", ")
   title = title.replace("Ω", "Ohm") # For release 892555.
   title = title.replace("•", ".") # For release 5550.
   title = title.replace("七人の侍", "The Seven Samurai") # For release 309.
   title = title.replace("複合", "Complex") # For release 309.
   return title

def normalize_catno(catno, release_id):
   catno = catno.replace("П", "_")
   catno = catno.replace("•", ".")
   catno = catno.replace("₂", "2")
   if catno == 'none':
      catno = 'r-' + str(release_id) # Generating a pseudo cat no from the discogs release ID; anything is better than "none".
   return catno

def NormalizeFileBaseName(name):
   name = name.replace("\"", "")
   name = name.replace("?", "")
   name = name.replace("¿", "")
   name = name.replace("!", "")
   name = name.replace("::", "__") # For release 619297.
   name = name.replace(": ", " - ")
   name = name.replace("\"", "")
   name = name.replace("/", "_")
   name = name.replace(">", "_")
   name = name.replace("<", "_")
   name = name.replace("|", "_")
   name = name.replace(":", "_")
   name = name.replace("*", "_")
   name = name.replace("Ω", "Ohm") # For release 892555.
   name = name.replace("•", ".") # For release 5550.
   name = name.replace("™", "(TM)") # For release 83942.
   name = name.replace("λ Lambda", "Lambda") # For release 78685.
   name = name.replace("フォーテック", "Photek") # For release 309.
   name = name.replace("七人の侍", "The Seven Samurai") # For release 309.
   name = name.replace("複合", "Complex") # For release 309.
   name = name.strip()
   return name

# def NormalizeShellArg(arg):
#    arg = arg.replace("\"", "\"\"") # doubling up quotes.
#    return arg

def TitleAndCatNoString(title, catno):
   titleAndCatno = ""
   if (len(title) == 0):
      titleAndCatno = catno
   else:
      titleAndCatno = title
      if not len(catno) == 0:
         titleAndCatno = titleAndCatno + " (" + catno + ")"
   if len(titleAndCatno) == 0:
      titleAndCatno = "Unknown"
   return titleAndCatno
