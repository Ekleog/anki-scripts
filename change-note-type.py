#!/usr/bin/env python

#################
# CONFIGURATION #
#################

# Beware! This script has been modified since I last used it, to make it more
# easily configurable. I may have introduced bugs in doing so.

# Currently, this script dumps the list of SQL requests that would be performed.
# Please check these are correct, then replace `print` by `c.execute` in the
# line following `# CHANGE HERE` in the implementation part of the script.

dbfile = "collection.anki2"

# Figure out the note types by clicking the note type in the browser: it's the
# lots-of-digits number after `mid:` that will appear in the search bar
from_notetype = "[TODO]"
to_notetype = "[TODO]"

def field_filter(flds):
    # For simple front/back note types where the order of fields hasn't changed
    return flds

    # For japanese note types that were (kanji, reading, meaning, notes) and
    # became (furiganaized_kanji, meaning, notes)
    #return [flds[0] + "[" + flds[1] + "]", flds[2], flds[3]]

    # For NihongoShark deck
    #kanji = flds[5] if flds[5] else flds[0]
    #reading = flds[6] if flds[6] else flds[1]
    #meaning = flds[8]
    #notes = flds[10]
    #return [kanji + "[" + reading + "]", meaning, notes]


##################
# IMPLEMENTATION #
##################

import anki
import hashlib
import sqlite3
import time

conn = sqlite3.connect(dbfile)
c = conn.cursor()
req = c.execute("SELECT id, flds FROM notes WHERE mid=" + from_notetype)
data = req.fetchall()

for x in data:
    id_ = x[0]
    old_flds = x[1].split("\x1f")

    flds = field_filter(old_flds)

    sfld = flds[0]
    csum = anki.utils.fieldChecksum(flds[0])
    flds = "\x1f".join(flds)

    # CHANGE HERE
    print(
        "UPDATE notes " +
        "SET mid=" + to_notetype + ", mod=:mod, usn=-1, flds=:flds, " +
            "sfld=:sfld, csum=:csum " +
        "WHERE id=:id",
        {   "mod": int(time.time()),
            "flds": flds,
            "sfld": sfld,
            "csum": csum,
            "id": id_,
        })

conn.commit()
