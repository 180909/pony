import re, sys, inspect, keyword, linecache, os.path #, cgitb, cStringIO

from repr import Repr
from itertools import izip, count

import pony
from pony import options, utils
from pony.utils import detect_source_encoding, is_ident, tostring, pos2lineno, getlines, getlines2
from pony.templating import html, cycle, quote, htmljoin, Html, StrHtml, ParseError

def restore_escapes(s):
    s = tostring(s)
    if not options.HTMLTB_RESTORE_ESCAPES: return s
    return utils.restore_escapes(s, 'utf-8').decode('utf-8')

addr_re = re.compile(r' at 0x[0-9a-fA-F]{8}(?:[0-9a-fA-F]{8})?>')

class Repr2(Repr):
    def __init__(self):
        Repr.__init__(self)
        self.maxstring = 76
        self.maxother = 76
    def repr_str(self, x, level):
        s = repr(x[:self.maxstring])
        s = restore_escapes(s)
        if len(s) > self.maxstring:
            i = max(0, (self.maxstring-3)//2)
            j = max(0, self.maxstring-3-i)
            s = repr(x[:i] + x[len(x)-j:])
            s = restore_escapes(s)
            s = s[:i] + '...' + s[len(s)-j:]
        return s
    repr_unicode = repr_str
    def repr1(self, x, level):
        typename = type(x).__name__
        if ' ' in typename: typename = '_'.join(typename.split())
        method = getattr(self, 'repr_' + typename, None)
        if method is not None: return method(x, level)
        try: s = repr(x)  # Bugs in x.__repr__() can cause arbitrary exceptions
        except: s = '<%s object at 0x%X>' % (x.__class__.__name__, id(x))
        s = restore_escapes(s)
        if options.HTMLTB_REMOVE_ADDR: s = addr_re.sub('>', s)
        return truncate(s, self.maxother)
    def repr_instance(self, x, level):
        try: s = repr(x)  # Bugs in x.__repr__() can cause arbitrary exceptions
        except: s = '<%s instance at 0x%X>' % (x.__class__.__name__, id(x))
        s = restore_escapes(s)
        if options.HTMLTB_REMOVE_ADDR: s = addr_re.sub('>', s)
        return truncate(s, self.maxstring)

def truncate(s, maxlen):
    if len(s) > maxlen:
        i = max(0, (maxlen-3)//2)
        j = max(0, maxlen-3-i)
        s = s[:i] + '...' + s[len(s)-j:]
    return s

aRepr2 = Repr2()
repr2 = aRepr2.repr

class Record(object):
    def __init__(self, **keyargs):
        self.moduletype = self.func = self.module = self.filename = self.fname = None
        self.__dict__.update(keyargs)
        filename = self.filename
        if filename and filename != '<?>': self.fname = os.path.split(filename)[1]

def format_exc(info=None, context=5):
    if info: exc_type, exc_value, tb = info
    else: exc_type, exc_value, tb = sys.exc_info()
    try:
        exc_msg = restore_escapes(exc_value)
        while tb.tb_next is not None:
            module = tb.tb_frame.f_globals.get('__name__') or '?'
            if module == 'pony' or module.startswith('pony.'): tb = tb.tb_next
            else: break
        records = []
        if issubclass(exc_type, SyntaxError) and exc_value.filename and exc_value.filename != '<?>':
            lines, index = getlines2(exc_value.filename, exc_value.lineno, context=5)
            source_encoding = detect_source_encoding(exc_value.filename)
            lines = [ format_line(None, line.decode(source_encoding, 'replace')) for line in lines ]
            record = Record(filename=exc_value.filename, lineno=exc_value.lineno, lines=lines, index=index)
            records = [ record ]
        else:
            frames = inspect.getinnerframes(tb, context)
            prev_frame = None
            for frame, filename, lineno, func, lines, index in frames:
                if index is None: continue
                source_encoding = detect_source_encoding(filename)
                lines = [ format_line(frame, line.decode(source_encoding, 'replace')) for line in lines ]
                module = frame.f_globals.get('__name__') or '?'
                if module == 'pony' or module.startswith('pony.'): moduletype = 'module-system'
                else: moduletype = 'module-user'
                record = Record(moduletype=moduletype, module=module, filename=filename,
                                lineno=lineno, func=func, lines=lines, index=index)
                records.append(record)
                if module != 'pony.templating': pass
                elif func in ('_eval', '_compile'):
                    element = prev_frame.f_locals['self']  # instance of SyntaxElement subclass
                    text, offsets, filename = (element.source + (None,))[:3]
                    lineno, offset = pos2lineno(element.start, offsets)
                    lines, index = getlines(text, offsets, lineno, context=5)
                    record = Record(filename=filename, lineno=lineno, lines=lines, index=index)
                    records.append(record)
                prev_frame = frame
            if issubclass(exc_type, ParseError):
                text, offsets = exc_value.source[:2]
                lines, index = getlines(text, offsets, exc_value.lineno, context=5)
                record = Record(lineno=exc_value.lineno, lines=lines, index=index)
                records.append(record)
        return html()
    finally: del tb

python_re = re.compile(r"""
        (                                        # string (group 1)
        (?:[Uu][Rr]?|[Rr][Uu]?)?                 #     string prefix 
        (?:                                      
            '''(?:[^\\]|\\.)*?(?:'''|\Z)         #     '''triple-quoted string'''
        |   \"""(?:[^\\]|\\.)*?(?:\"""|\Z)       #     \"""triple-quoted string\"""
        |   '(?:[^'\\]|\\.)*?'                   #     'string'
        |   "(?:[^"\\]|\\.)*?"                   #     "string"
        ))
    |   ([A-Za-z_]\w*(?:\s*\.\s*[A-Za-z_]\w*)*)  # identifier chain (group 2)
    |   (\#.*$)                                  # comment (group 3)
    """, re.VERBOSE)
           

ident_re = re.compile(r'[A-Za-z_]\w*')
end1_re = re.compile(r"(?:[^\\]|\\.)*?'''")
end2_re = re.compile(r'(?:[^\\]|\\.)*?"""')

ident_html = StrHtml('<span class="ident" title="%s">%s</span>')
keyword_html = StrHtml('<strong>%s</strong>')
comment_html = StrHtml('<span class="comment">%s</span>')
str_html = StrHtml('<span class="string">%s</span>')

__undefined__ = object()

def format_line(frame, line):
    if frame is not None:
        f_locals = frame.f_locals
        f_globals = frame.f_globals
    else: f_locals = f_globals = {}
    result = []
    pos = 0
    end = len(line)
    while pos < end:
        match = python_re.search(line, pos)
        if match is None: break
        result.append(quote(line[pos:match.start()]))
        i = match.lastindex
        if i == 1: result.append(str_html % match.group())
        elif i == 2:
            chain = []
            prev = __undefined__
            for x in re.split('(\W+)', match.group()):
                if x in keyword.kwlist: result.append(keyword_html % x)
                elif is_ident(x):
                    if not chain:
                        obj = f_locals.get(x, __undefined__)
                        if obj is __undefined__: obj = f_globals.get(x, __undefined__)
                        if obj is __undefined__:
                            builtins = f_globals.get('__builtins__')
                            if isinstance(builtins, dict): obj = builtins.get(x, __undefined__)
                            else: obj = getattr(builtins, x, __undefined__)
                    else:
                        prev = chain[-1]
                        if prev is __undefined__: obj = __undefined__
                        else: obj = getattr(prev, x, __undefined__)
                    chain.append(obj)
                    if obj is __undefined__: title = 'undefined'
                    else: title = quote(repr2(obj))
                    result.append(ident_html % (title, x))
                else: result.append(quote(x))
        elif i == 3: result.append(comment_html % match.group())
        else: assert False
        pos = match.end()
    result.append(quote(line[pos:]))
    return htmljoin(result)

##def format_exc():
##    exc_type, exc_value, traceback = sys.exc_info()
##    try:
##        io = cStringIO.StringIO()
##        hook = cgitb.Hook(file=io)
##        hook.handle((exc_type, exc_value, traceback))
##        return io.getvalue()
##    finally: del traceback