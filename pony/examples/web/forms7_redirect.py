# -*- coding: cp1251 -*-
from pony.main import *

use_autoreload()

@http('/')
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
        return f

@http('/success')
def page2():
    return html(u"<h4>�������� ��������� �������</h4>")


http.start()    