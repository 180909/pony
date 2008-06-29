# coding: cp1251

import re, os.path

from pony.utils import read_text_file

ALPHABET = set(u"��������������������������������")
VOVELS = u"���������"

if __name__ != '__main__':
    stopwords_filename = os.path.join(os.path.dirname(__file__), 'stopwords-ru.txt')
    stopwords = set(read_text_file(stopwords_filename).split())

basic_endings = set(u"""
� �� ��� �� �� � �� ��� �� �� �� ��� � �� �� �� �� ��� �� �� � � ��
��� �� �� �� ��� � �� � �� �� �� ��� �� � �� � �� � �� ��� �� �� ��
""".split())

def basic_stem(word):
    # Basic stemming. Approximate 5x faster then snowball_stem(word)
    
    # word = word.lower().replace(u'�', u'�')
    size = len(word)
    if size > 5 and word[-3:] in basic_endings: return word[:-3]
    if size > 4 and word[-2:] in basic_endings: return word[:-2]
    if size > 3 and word[-1:] in basic_endings: return word[:-1]
    return word

def regex(s):
    return re.compile(s, re.UNICODE)

def grouped(s):
    return u"(?:%s)" % s

rPGERUND    = grouped(u"(?:(?:��)?��)?�(?:[��]|(?=[��]))")
rADJECTIVE  = grouped(u"[���][����]|��[��]|��[��]|��[��]|�[��]|�[����]|�[��]")
rPARTICIPLE = grouped(u"���|��[��]|(?:��|��|��|��?)(?=[��])")
rADJECTIVAL = "%s%s?" % (rADJECTIVE, rPARTICIPLE)
rREFLEXIVE  = grouped(u"[��]�")
rVERB1      = u"(?:�[��]|��[��]|��|�|�|��|�|�(?:�|��?)|�[��]|��|�(?:�|��))(?=[��])"
rVERB2      = u"�(?:�[��]|��)|��(?:�|�[��])|��[��]|�[��]|�[��]|�[��]|��|�(?:��|�[��])|�(?:[���]|[��]�)|���|�(?:��|�[��])|��?"
rVERB       = grouped(rVERB1 + '|' + rVERB2)
rNOUN       = grouped(u"[�����]|�[��]|�[��]?|��(?:�|��?)|�[��]?|�(?:[��]|��?)?|�(?:[��]|[��]�?)|�(?:�|��?)|�[��]?|�[��]?")
rSUPERLATIVE  = grouped(u"�?���")
rDERIVATIONAL = u"�?���"

STEP1 = u"(?:%s|%s?(?:%s|%s|%s)?)" % (rPGERUND, rREFLEXIVE, rADJECTIVAL, rVERB, rNOUN)
STEP2 = u"�?"
STEP3 = u"(?:�?���(?=[^@]+[@]+[^@]))?".replace('@', VOVELS)
STEP4 = u"(?:�|%s?(?:�(?=�))?)?" % rSUPERLATIVE
stem_re = regex(STEP1+STEP2+STEP3+STEP4)
word_re = regex(ur"^[�-�]+$")
rv_re = regex(ur"([^@]*[@])(.*)".replace('@', VOVELS))

def snowball_stem(word):
    # Based on http://snowball.tartarus.org/algorithms/russian/stemmer.html

    # word = word.lower().replace(u'�', u'�')
    if not word_re.match(word): return word
    rv_match = rv_re.match(word)
    if not rv_match: return word
    prefix, rv = rv_match.groups()
    revrv = rv[::-1]
    ending = stem_re.match(revrv).group()
    rest = revrv[len(ending):]
    return prefix + rest[::-1]

PGERUND = u"*� *��� *����� �� ���� ������ �� ���� ������".split()
ADJECTIVE = u"�� �� �� �� ��� ��� �� �� �� �� �� �� �� �� ��� ��� ��� ��� �� �� �� �� �� �� �� ��".split()
PARTICIPLE = u"*�� *�� *�� *�� *� ��� ��� ���".split()
VERB = u"""
*�� *�� *��� *��� *�� *� *� *�� *� *�� *�� *�� *�� *�� *�� *��� *���
��� ��� ��� ���� ���� ��� ��� ��� �� �� �� �� �� �� �� ��� ��� ��� �� ��� ��� ��  �� ��� ��� ��� ��� �� �
""".split()
REFLEXIVE = u"�� ��".split()
NOUN = u"� �� �� �� �� � ���� ��� ��� �� �� � ��� �� �� �� � ��� �� ��� �� �� �� � � �� ��� �� � � �� �� � �� �� �".split()
SUPERLATIVE = u"��� ����".split()
DERIVATIONAL = u"��� ����".split()

def _generate_endings():
    adjectival = ADJECTIVE + [ p+a for p in PARTICIPLE+[u"���"] for a in ADJECTIVE ]
    adjectival = [ x for x in adjectival if u'��' not in x ]
    verb_reflexive = VERB + [ v+r for v in VERB for r in REFLEXIVE ]
    all = PGERUND + adjectival + verb_reflexive + NOUN
    all += [ u"�"+x for x in all if x[0] not in u'*���' ] + [u"����"]
    d = {}
    for x in all:
        if u'����' in x or u'����' in x: continue
        if x.startswith('*'):
            d[u'�' + x[1:]] = 1
            d[u'�' + x[1:]] = 1
        else:
            d[x] = 0
            if len(x) < 5: d[u'��' + x] = 1
            if len(x) < 6: d[u'�' + x] = 0
    return d

endings = _generate_endings()

def fast_stem(word):
    # Approximate 2x faster then snowball_stem(word)

    # word = word.lower().replace(u'�', u'�')    
    for i in xrange(min(6, len(word)-2), 0, -1):
        x = endings.get(word[-i:])
        if x is not None: return word[:-i+x]
    return word

stem = fast_stem

if __name__ == '__main__':
    words = []
    text = read_text_file('stemmingtest-ru.txt')
    for line in text.split('\n'):
        if not line or line.isspace(): continue
        word, expected = line.split()
        words.append(word)
        a = snowball_stem(word)
        b = fast_stem(word)
        if not (a == b == expected): print word, expected, a, b

    import timeit
    t1 = timeit.Timer('[ stem(word) for word in words ]', 'from __main__ import snowball_stem as stem, words')
    t2 = timeit.Timer('[ stem(word) for word in words ]', 'from __main__ import fast_stem as stem, words')
    t3 = timeit.Timer('[ stem(word) for word in words ]', 'from __main__ import basic_stem as stem, words')
    print min(t1.repeat(5, 1000))
    print min(t2.repeat(5, 1000))
    print min(t3.repeat(5, 1000))

    raw_input()
    