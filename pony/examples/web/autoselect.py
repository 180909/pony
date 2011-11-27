# coding: cp1251

from pony.main import *

use_autoreload()

@http('/')
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
            if f.city.value: return html(u'''
                <h1>���������:</h1>
                <h2>���������: @f.continent.value</h2>
                <h2>������: @f.country.value</h2>
                <h2>�����: @f.city.value</h2>
                ''')
    return f

http.start()    
