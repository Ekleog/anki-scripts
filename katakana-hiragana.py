# This isn't really a script, just something I extracted from
# rationalize-furigana.py because I had a use case for it at some point and could
# need it again. Basically was used to convert katakana to hiragana. as part of
# one of the other scripts.

hira = u'がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ' + \
       u'あいうえおかきくけこさしすせそたちつてと' + \
       u'なにぬねのはひふへほまみむめもやゆよらりるれろ' + \
       u'わをんぁぃぅぇぉゃゅょっ'
kata = u'ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポ' + \
       u'アイウエオカキクケコサシスセソタチツテト' + \
       u'ナニヌネノハヒフヘホマミムメモヤユヨラリルレロ' + \
       u'ワヲンァィゥェォャュョッ'
def kata2hira(s):
    return s.translate({ord(kata[i]): hira[i] for i in range(len(hira))})
