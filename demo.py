# -*- coding: utf-8 -*-

from codecs import open
from itertools import imap
from math import log

from lexicon import Lexicon
from segment import Segmenter


def wrap(line):
    w, f = line.strip().split(' ')
    f = log(float(f) + 1.0)
    return (w, f)


with open('dict.txt', 'r', 'utf-8') as fin:
    tf = dict(imap(wrap, fin))
    lex = Lexicon(tf)
    seg = Segmenter(lex)
    result = seg.segment(u'這是一隻可愛的小花貓')
    print '/'.join(result).encode('utf-8')
