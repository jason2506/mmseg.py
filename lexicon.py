# -*- coding: utf-8 -*-


def _create_trie(words):
    trie = {}
    for word in words:
        ptr = trie
        for char in word:
            if char not in ptr:
                ptr[char] = {}

            ptr = ptr[char]

        ptr[''] = ''

    return trie


class Lexicon(object):
    def __init__(self, tf):
        self._trie = _create_trie(tf.iterkeys())
        self._tf = tf

    def term_frequency(self, term):
        return self._tf.get(term, 0)

    def get_chunks(self, string, start=0, max_len=3):
        str_len = len(string)
        if max_len == 0 or start == str_len:
            yield tuple()
        else:
            ptr = self._trie
            for i in xrange(start, str_len):
                if string[i] not in ptr:
                    break

                ptr = ptr[string[i]]
                if '' in ptr:
                    for chunk in self.get_chunks(string, i + 1, max_len - 1):
                        yield (string[start:i + 1],) + chunk
