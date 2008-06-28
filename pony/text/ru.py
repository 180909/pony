# coding: cp1251

import re, os.path

from pony.utils import read_text_file

stopwords_filename = os.path.join(os.path.dirname(__file__), 'stopwords-ru.txt')
stopwords = set(read_text_file(stopwords_filename).split())

endings = u"""
� �� ��� �� �� � �� ��� �� �� �� ��� � �� �� �� �� ��� �� �� � � ��
��� �� �� �� ��� � �� � �� �� �� ��� �� � �� � �� � �� ��� �� �� ��
""".split()

endings_1 = set(x for x in endings if len(x) == 1)
endings_2 = set(x for x in endings if len(x) == 2)
endings_3 = set(x for x in endings if len(x) == 3)

def basicstem(word):
    "Basic stemming. Approximate 10x faster then stem(word)"
    size = len(word)
    if size > 5 and word[-3:] in endings_3: return word[:-3]
    if size > 4 and word[-2:] in endings_2: return word[:-2]
    if size > 3 and word[-1:] in endings_1: return word[:-1]
    return word

def regex(s):
    return re.compile(s, re.UNICODE)

def grouped(s):
    return u"(?:%s)" % s

PGERUND    = grouped(u"(?:(?:��)?��)?�(?:[��]|(?=[��]))")
ADJECTIVE  = grouped(u"[���][����]|��[��]|��[��]|��[��]|�[��]|�[����]|�[��]")
PARTICIPLE = grouped(u"���|��[��]|(?:��|��|��|��?)(?=[��])")
ADJECTIVAL = "%s%s?" % (ADJECTIVE, PARTICIPLE)
REFLEXIVE  = grouped(u"[��]�")
VERB1      = u"(?:�[��]|��[��]|��|�|�|��|�|�(?:�|��?)|�[��]|��|�(?:�|��))(?=[��])"
VERB2      = u"�(?:�[��]|��)|��(?:�|�[��])|��[��]|�[��]|�[��]|�[��]|��|�(?:��|�[��])|�(?:[���]|[��]�)|���|�(?:��|�[��])|��?"
VERB       = grouped(VERB1 + '|' + VERB2)
NOUN       = grouped(u"[�����]|�[��]|�[��]?|��(?:�|��?)|�[��]?|�(?:[��]|��?)?|�(?:[��]|[��]�?)|�(?:�|��?)|�[��]?|�[��]?")
SUPERLATIVE  = grouped(u"�?���")
DERIVATIONAL = u"�?���"

VOVELS = u"���������"
STEP1 = u"(?:%s|%s?(?:%s|%s|%s)?)" % (PGERUND, REFLEXIVE, ADJECTIVAL, VERB, NOUN)
STEP2 = u"�?"
STEP3 = u"(?:�?���(?=[^@]+[@]+[^@]))?".replace('@', VOVELS)
STEP4 = u"(?:�|%s?(?:�(?=�))?)?" % SUPERLATIVE
stem_re = regex(STEP1+STEP2+STEP3+STEP4)
word_re = regex(ur"^[�-�]+$")
rv_re = regex(ur"([^@]*[@])(.*)".replace('@', VOVELS))

def stem(word):
    # Based on http://snowball.tartarus.org/algorithms/russian/stemmer.html
    word = word.lower().replace(u'�', u'�')
    if not word_re.match(word): return word
    rv_match = rv_re.match(word)
    if not rv_match: return word
    prefix, rv = rv_match.groups()
    revrv = rv[::-1]
    ending = stem_re.match(revrv).group()
    rest = revrv[len(ending):]
    return prefix + rest[::-1]

if __name__ == '__main__':
    text = read_text_file('test-ru.txt')
    for line in text.split('\n'):
        if not line or line.isspace(): continue
        word, expected = line.split()
        s = stem(word)
        if s != expected: print 'failed: %s (expected: %s, got: %s)' % (word, expected, s)
    print 'done'
    raw_input()
