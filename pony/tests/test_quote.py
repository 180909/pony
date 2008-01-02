# -*- encoding: cp1251 -*-

from pony.templating import quote, Html, StrHtml

class C1(object):
    def __unicode__(self):
        return Html(u'<z&"�>')
    def __str__(self):
        return 'incorrect'

class C2(object):
    def __unicode__(self):
        return u'<z&"�>'
    def __str__(self):
        return 'incorrect'

class C3(object):
    def __str__(self):
        return StrHtml('<z&"�>')

class C4(object):
    def __str__(self):
        return '<z&"�>'

data = [
    (1, 1, 1),
    (1000000000000, 1000000000000, 1000000000000),
    (1.0, 1.0, 1.0),
    (Html(u'<z&"�>'), Html(u'<z&"�>'), Html(u'<z&"�>')),
    (C1(), Html(u'<z&"�>'), Html(u'<z&"�>')),
    (C2(), Html(u'&lt;z&amp;&quot;�&gt;'), Html(u'&lt;z&amp;&quot;�&gt;')),
    (C3(), StrHtml('<z&"�>'), Html(u'<z&"\ufffd>')),
    (C4(), StrHtml('&lt;z&amp;&quot;�&gt;'), Html(u'&lt;z&amp;&quot;\ufffd&gt;')),
    ]

def test_quote():
    for i, (input, expected1, expected2) in enumerate(data):
        result = quote(input)
        if result != expected1:
            print i, 1, input, expected1, result
            assert False
        result = quote(input, True)
        if result != expected2:
            print i, 2, input, expected2, result
            assert False
    print 'Test passed!'

if __name__ == '__main__':
    test_quote()
    import time; time.sleep(1)
    
