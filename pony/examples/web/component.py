# coding: cp1251

from pony.main import *

@component(css="mycss.css", js=["myscipt1.js", "myscript2.js"])
def my_component(content):
    return html('<div class="my_class">@content</div>')

@http('/')
def index():
    return html(u'''
    <title>������ ������������� ����������</title>
    <h1>��� ���������</h1>
    @my_component("Hello")
    @my_component{������ ������������� ����������}
    <p>��� ������ �����</p>
    ''')

http.start()
