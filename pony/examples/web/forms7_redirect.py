# -*- coding: cp1251 -*-
from pony.main import *

use_autoreload()

@webpage('/')
def page1():
    f = Form()
    f.msg = StaticText(u'������� ����� ����� �������')
    f.from_account = Text(u'�')
    f.to_account = Text(u'��')
    f.amount = Text(u'�����')
    f.sbm = Submit()
    if f.is_valid:
        raise http.Redirect('/success')
    else:
        print f

@webpage('/success')
def page2():
    print u"<h4>�������� ��������� �������</h4>"


http.start()    