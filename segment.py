# -*- coding: utf-8 -*-

from abc import ABCMeta
from itertools import imap, ifilter
from re import compile

__all__ = ('Segmenter',)


def _chunk_len(chunk):
    return sum(imap(len, chunk))


def _chunk_avg_len(chunk):
    return sum(imap(len, chunk)) / float(len(chunk))


def _chunk_var_len(chunk):
    avg_len = _chunk_avg_len(chunk)
    squares = imap(lambda c: (len(c) - avg_len) ** 2, chunk)
    return sum(squares) / float(len(chunk))


def _chunk_tf_sum(lex):
    def calculate_sum(chunk):
        chunk = ifilter(lambda w: len(w) == 1, chunk)
        tf_list = imap(lex.term_frequency, chunk)
        return sum(tf_list)

    return calculate_sum


def _create_rule(func, get_max=True):
    def rule(chunks):
        max_or_min = get_max and max or min
        target = max_or_min(imap(func, chunks))
        return lambda c: func(c) == target

    return rule


class _HandlerBase(object):
    __metaclass__ = ABCMeta

    def match(self, string):
        return self.__class__._PTN.match(string)

    def process(self, token):
        yield token


class _SpaceHandler(_HandlerBase):
    _PTN = compile(ur'\s+')

    def process(self, token):
        # do nothing
        return
        yield


class _EnglishAndNumberHandler(_HandlerBase):
    _PTN = compile(ur'[A-Za-z0-9]+')


class _HalfWidthSymbolHandler(_HandlerBase):
    _PTN = compile(ur'[\u0021-\u002F\u003A-\u0040\u005B-\u0060\u007B-\u007E]+')


class _PunctuationHandler(_HandlerBase):
    _PTN = compile(ur'[\u3000-\u303F\uFF00-\uFFEF]+')


class _ChineseWordHandler(_HandlerBase):
    _PTN = compile(ur'[\u4E00-\u9FFF]+')

    def __init__(self, lex):
        self._lex = lex
        self._rules = [_create_rule(_chunk_len),
                       _create_rule(_chunk_avg_len),
                       _create_rule(_chunk_var_len, get_max=False),
                       _create_rule(_chunk_tf_sum(lex))]

    def process(self, token):
        token_len = len(token)
        start = 0
        while start < token_len:
            chunks = tuple(self._lex.get_chunks(token, start))
            for rule in self._rules:
                if len(chunks) == 1:
                    break

                chunks = filter(rule(chunks), chunks)

            assert len(chunks) == 1
            word = chunks[0][0]
            start += len(word)
            yield word


class Segmenter(object):
    def __init__(self, lex):
        self._handlers = [_ChineseWordHandler(lex),
                          _EnglishAndNumberHandler(),
                          _HalfWidthSymbolHandler(),
                          _PunctuationHandler(),
                          _SpaceHandler()]

    def segment(self, string):
        while string != '':
            processed = False
            for handler in self._handlers:
                match = handler.match(string)
                if match is not None:
                    for token in handler.process(match.group(0)):
                        yield token

                    string = string[match.end(0):]
                    processed = True

            if not processed:
                yield string[0]
                string = string[1:]
