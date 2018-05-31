#!/usr/bin/env python3

# No-configuration script, will output as a CSV the parsed vocabulary list from
# https://github.com/Wizcorp/japanese-dev-lingo/blob/master/ReadMe.md

# The output CSV has fields: (kanji, reading, english, notes)

# This is designed to be used in a pipeline like:
#   ./import-wizcorp-vocab-list.py | ./furiganaize.py > to_import.csv
# Then hand-verification of `to_import.csv` looking good and finally import into
# Anki

from urllib.request import urlopen
import csv
import sys

url = "https://raw.githubusercontent.com/Wizcorp/japanese-dev-lingo/master/ReadMe.md"

src = urlopen(url).read().decode('utf-8')
out = csv.writer(sys.stdout)

for line in src.split('\n'):
    word = line.split('|')
    if len(word) != 4 or (word[0] == 'English ' and word[1] == ' Japanese ') or word[0][0] == '-':
        continue
    word[0] = word[0].lower()
    word = [w.strip() for w in word]
    [english, japanese, kana, notes] = word
    out.writerow([japanese, kana, english, notes])
