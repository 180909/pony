# -*- coding: cp1251 -*-
from pony.main import *

use_autoreload()

@http('/')
def page1():
    f1 = Form(name='form1')
    f1.msg = StaticText(u'��������� �����')
    f1.rating = Text(u'�������', type=int)
    f1.sbm = Submit(u'�������������')
    f2 = Form(name='form2')
    f2.msg = StaticText(u'������������ �����')
    f2.rating = Text(u'�������',type=int)
    f2.sbm = Submit(u'�������������')

    forms = [ f1, f2 ]
    for f in forms:
        if f.is_valid:
            return html(u'<h4>�����: @f.msg.value  �������: @f.rating.value</h4>')

    return html('''
        @for(f in forms)
        {
            @f
        }
    ''')

http.start()    