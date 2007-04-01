# -*- encoding: cp1251 -*-

from pony.main import *

@http("/")
def main():
    return html(u'''
        <ul>
            <li>$link(page1)
            <li><a href="/%D0%BF%D1%80%D0%BE%D0%B2%D0%B5%D1%80%D0%BA%D0%B0"
                >�������� 2</a>
            <li><a href="/��������">�������� 3</a>
            <li>$link(form_page)
            <li>$link(cp1251)
            <li>$link(utf8)
        </ul>
    ''')

@http(u"/��������")
def page1():
    u"�������� ��������"
    return html(u'''
        <h1>�������� ��������</h1>
    ''')

@http(u"/�����?firstname=$name")
def form_page(name=None):
    u"�������� �����"
    return html(u'''
        $if(name is None) { <h1>��� ���� ���, ����?</h1> }
        $else { <h1>Hello, $(name)!</h1> }
        <form>
            <label for="firstname">���: </label>
            <input type="text" id="firstname" name="firstname"
                   value="$(name or '')">
            <input type="submit" value="���������!">
        </form>
    ''')

@http
def cp1251():
    u"������ �������� � ��������� cp1251"
    return html(encoding='cp1251')

@http
def utf8():
    u"������ �������� � ��������� utf8"
    return html()

start_http_server('localhost:8080')

