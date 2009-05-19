# coding: cp1251

from pony.main import *

use_autoreload()

@webpage('/')
def index():
    f = Form()
    f.continent = AutoSelect(u'���������', options=[ (None, u'<�������� ���������>'), u'�������', u'�������' ])
    if f.continent.value:
        if f.continent.value == u'�������': countries = [ u'���', u'��������' ]
        elif f.continent.value == u'�������': countries = [ u'������', u'�������' ]
        f.country = AutoSelect(u'������', options= [ (None, u'<�������� ������>') ] + countries)
        if f.country.value:
            if f.country.value == u'���': cities = [ u'���-����', u'���-��������', u'���������' ]
            elif f.country.value == u'��������': cities = [ u'���-��-�������', u'����-��������', u'��������' ]
            elif f.country.value == u'�������': cities = [ u'�����', u'����', u'�������' ]
            elif f.country.value == u'������': cities = [ u'������', u'�����-���������', u'��������' ]
            f.city = AutoSelect(u'�����', options=[ (None, u'<�������� �����>') ] + cities)
            if f.city.value:
                print u'<h1>���������:</h1>'
                print u'<h2>���������: %s</h2>' % f.continent.value
                print u'<h2>������: %s</h2>' % f.country.value
                print u'<h2>�����: %s</h2>' % f.city.value
    print f

http.start()    
