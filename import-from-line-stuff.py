#!/usr/bin/env python3

# Parameters, in order:
#  * The input, which is eg. the output of `pdftotext` from a kanji manual
#  * Name of the output for found vocabulary words (eg. vocab.csv)

# `vocab.csv` has fields: (kanji, reading, meaning, notes)

# This script is interactive.

import csv
import sys
import termios
import tty

srcfile = sys.argv[1]
vocabfile = sys.argv[2]

with open(srcfile, 'r') as srcf:
    src = [l[:-1] for l in srcf.readlines()]
vocab = csv.writer(open(vocabfile, 'a'))

old_settings = termios.tcgetattr(sys.stdin.fileno())
tty.setcbreak(sys.stdin.fileno())

l = 0
card = ["", "", "", ""]
field = 0
stash = []
while True:
    if l >= len(src):
        l = len(src) - 1
    if l < 0:
        l = 0

    line = src[l]
    if line == "":
        l += 1
        continue

    print("\nStash status:")
    if stash == []:
        print(" -> empty")
    for c in stash:
        print(" * " + str(c))

    print("\nRead ‘\033[36;1m" + line + "\033[0m’ with card [", end = "")
    for (f, v) in enumerate(card):
        if f == field:
            print("\033[31;1;4m", end = "")
        print(repr(v), end = "")
        if f == field:
            print("\033[0m", end = "")
        if f != 3:
            print(", ", end = "")
    print("]")

    print("Action?\n"
        + "[\033[31;1;4ms\033[0m]kip [\033[31;1;4ma\033[0m]dd_to_field "
            + "[\033[31;1;4mn\033[0m]ext_field next_[\033[31;1;4mC\033[0m]ard\n"
        + "s[\033[31;1;4mt\033[0m]ash_card [\033[31;1;4mr\033[0m]otate_stash "
            + "[\033[31;1;4mD\033[0m]rop_card\n"
        + "[\033[31;1;4mm\033[0m]ark_card [\033[31;1;4mM\033[0m]ark_location "
            + "[\033[31;1;4md\033[0m]efine_field\n"
        + "[\033[31;1;4mp\033[0m]rev_field "
            + "[\033[31;1;4mb\033[0m]ack_to_prev_line\n"
        + "[\033[31;1;4mE\033[0m]xit\n"
        + " -> Choice: ", end = "")
    sys.stdout.flush()
    c = sys.stdin.read(1)
    print(c)

    if c == 's':
        l += 1
    elif c == 'a':
        card[field] += line
    elif c == 'n':
        field = (field + 1) % 4
    elif c == 'C':
        vocab.writerow(card)
        card = ["", "", "", ""]
        field = 0
    elif c == 't':
        stash = [(card, field)] + stash
        card = ["", "", "", ""]
        field = 0
    elif c == 'r':
        stash = [(card, field)] + stash
        card, field = stash[-1]
        stash = stash[:-1]
    elif c == 'D':
        if stash != []:
            card, field = stash[-1]
            stash = stash[:-1]
    elif c == 'm':
        card[3] = "XXX"
    elif c == 'M':
        vocab.writerow(["XXX"])
    elif c == 'd':
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)
        print("Please enter field value: ", end = "")
        sys.stdout.flush()
        card[field] = input()
        tty.setcbreak(sys.stdin.fileno())
    elif c == 'p':
        field = (field + 3) % 4
    elif c == 'b':
        l -= 1
        while l >= 0 and src[l] == "":
            l -= 1
    elif c == 'E':
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)
        print("Are you sure you want to exit? (yes/no) ", end = "")
        sys.stdout.flush()
        inp = input()
        if inp == 'yes':
            print("Delete handled lines from the input file? (yes/no) ", end = "")
            sys.stdout.flush()
            inp = input()
            if inp == 'yes':
                with open(srcfile, 'w') as srcf:
                    while l < len(src):
                        srcf.write(src[l] + '\n')
                        l += 1
                sys.exit(0)
            elif inp == 'no':
                sys.exit(0)
            else:
                print("Did not get 'yes' nor 'no', returning to loop")
        else:
            print("Did not get 'yes', returning to loop")
        tty.setcbreak(sys.stdin.fileno())
    else:
        print("Did not understand the command!")
