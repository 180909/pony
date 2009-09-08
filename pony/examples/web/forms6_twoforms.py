# -*- coding: cp1251 -*-
from pony.main import *

use_autoreload()

@webpage('/')
def page1():
    f1 = Form(name='form1')
    f1.msg = StaticText(u'��������� �����')
    f1.rating = Text(u'�������', type=int)
    f1.sbm = Submit(u'�������������')
    f2 = Form(name='from2')
    f2.msg = StaticText(u'������������ �����')
    f2.rating = Text(u'�������',type=int)
    f2.sbm = Submit(u'�������������')

    for f in [f1, f2]:
        if f.is_valid:
            raise http.Redirect(url(success, f.msg.value, f.rating.value))
        else:
            print f

@webpage
def success(movie, rating):
    print u"<h4>�����:%s  �������:%s</h4>" % (movie, rating)


http.start()    