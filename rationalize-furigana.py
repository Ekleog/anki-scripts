#!/usr/bin/env python
# -*- coding: utf-8 -*-

#################
# CONFIGURATION #
#################

# Beware! This script is currently a mess: I used it to rationalize a lot of
# stuff before starting this anki-scripts repos. The good thing is that it can
# do quite a lot. The bad thing is that there may be code that no longer even
# works. Please check attentively the results proposed before doing any change.
# And do make sure to have a backup of your database in case anything goes
# wrong.

# This scripts takes a note type that's assumed to have furaganaized kanji as
# the first field (see the various `# ASSUMPTION FURIGANA FIRST FIELD` in the
# implementation), and to have three fields (see `# ASSUMPTION NUMBER OF FIELDS`
# below).

# The input note type's first fields are assumed to be like 食べる[たべる] (eg.
# as the result of running `change-note-type.py`). It will then try to match the
# hiragana together and end up with 食[た]べる, for a cleaner display. It should
# ignore note types that are not like KANJI[READING], and should ask for
# confirmation before any change.

# Please first check the proposed SQL requests look good before replacing
# `print` with `c.execute` at the `# CHANGE HERE` point.

dbfile = "collection.anki2"

# Figure out the note types by clicking the note type in the browser: it's the
# lots-of-digits number after `mid:` that will appear in the search bar
notetype = "[TODO]"


##################
# IMPLEMENTATION #
##################

import anki
import copy
import hashlib
import re
import sqlite3
import string
import time

def match_strs(a, b):
    POISON = [([u"😞"], [u"😞"])]
    tab = [[None for _ in range(len(b) + 1)] for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        tab[i][0] = (0, [(list(a[:i]), [])])
    for j in range(len(b) + 1):
        tab[0][j] = (0, [([], list(b[:j]))])
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            eq = (-1, POISON)
            if a[i - 1] == b[j - 1]:
                eq = (tab[i - 1][j - 1][0] + 1,
                      tab[i - 1][j - 1][1] + [([a[i - 1]], [b[j - 1]]), ([], [])])
                if tab[i - 1][j - 1][1] == POISON:
                    eq = (eq[0], POISON)
            if eq[0] > tab[i - 1][j][0] and eq[0] > tab[i][j - 1][0]:
            #if eq[0] >= tab[i - 1][j][0] and eq[0] >= tab[i][j - 1][0]: # comment below elif if uncommenting this
                tab[i][j] = eq
            elif eq[0] == tab[i - 1][j][0] or eq[0] == tab[i][j - 1][0]:
                tab[i][j] = (eq[0], POISON)
            elif tab[i - 1][j][0] > tab[i][j - 1][0]:
                tab[i][j] = copy.deepcopy(tab[i - 1][j])
                if tab[i][j][1] != POISON:
                    tab[i][j][1][-1][0].append(a[i - 1])
            else:
                tab[i][j] = copy.deepcopy(tab[i][j - 1])
                if tab[i][j][1] != POISON:
                    tab[i][j][1][-1][1].append(b[j - 1])
    if tab[len(a)][len(b)][1] == POISON:
        return [(a, b)]
    res = []
    for (aa, bb) in tab[len(a)][len(b)][1]:
        res.append(("".join(aa), "".join(bb)))
    return res

def furiganaize(kanji, reading):
    res = u""
    for (k, r) in match_strs(kanji, reading):
        if k == r or r == '':
            res += k
        else:
            res += " " + k + "[" + r + "]"
    res = re.sub(' +', ' ', res)
    return res.strip()

conn = sqlite3.connect(dbfile)
c = conn.cursor()
req = c.execute("SELECT id, flds FROM notes WHERE mid=" + notetype)
data = req.fetchall()

for x in data:
    id_ = x[0]
    old_flds = x[1].split("\x1f")

    if old_flds[0][-1] != "]" or old_flds[0].count("[") != 1:
        continue

    # ASSUMPTION FURIGANA FIRST FIELD
    kanji = old_flds[0].split("[")[0]
    reading = old_flds[0].split("[")[1][:-1]

    new_jp = furiganaize(kanji, reading)

    if new_jp == old_flds[0]:
        continue

    doit = None
    while doit == None:
        # ASSUMPTION FURIGANA FIRST FIELD
        print "Replace “{}” with “{}”? (y/n/q) ".format(
                old_flds[0].encode('utf-8'), new_jp.encode('utf-8')),
        i = raw_input()
        if i == 'y':
            doit = True
        elif i == 'n':
            doit = False
        elif i == 'q':
            doit = "break"
    if not doit:
        continue
    elif doit == "break":
        break

    # ASSUMPTION FURIGANA FIRST FIELD
    # ASSUMPTION NUMBER OF FIELDS
    flds = [new_jp, old_flds[1], old_flds[2]]
    sfld = flds[0]
    csum = anki.utils.fieldChecksum(flds[0])
    flds = "\x1f".join(flds)

    # CHANGE HERE
    print(
        "UPDATE notes " +
        "SET mod=:mod, usn=-1, flds=:flds, sfld=:sfld, csum=:csum " +
        "WHERE id=:id",
        {   "mod": int(time.time()),
            "flds": flds,
            "sfld": sfld,
            "csum": csum,
            "id": id_,
        })

conn.commit()
