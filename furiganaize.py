#!/usr/bin/env python3

# No-configuration script, takes as input a CSV in
# (kanji, reading, english, notes) format, and outputs a furigana-ized CSV in
# format (furigana-ized kanji, english, notes)

import copy
import csv
import re
import sys

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

src = csv.reader(sys.stdin)
out = csv.writer(sys.stdout)

for [kanji, reading, english, notes] in src:
    out.writerow([furiganaize(kanji, reading), english, notes])
