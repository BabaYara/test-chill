import collections
import os
import os.path
import itertools
import re

from . import util

if util.python_version_major == 2:
    from HTMLParser import HTMLParser
else:
    from html.parser import HTMLParser


class TestFunction(object):
    def __init__(self, name, return_type, parameters):
        self.name = name
        self.return_type = return_type
        self.parameters = parameters


class TestCodeParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'test':
            self._readin = True
    
    def handle_endtag(self, tag):
        if tag == 'test':
            self._readin = False
    
    def handle_data(self, txt):
        if self._readin:
            self._value += txt
    
    @classmethod
    def parse(cls, txt):
        reader = cls()
        reader._readin = False
        reader._value = ''
        reader.feed(txt)
        func, _ = reader._parse_testprocedure(txt)
        return func


class TestCodeGenerator(object):
    _comment_style_expr = {
            'c':      [('/(/)+',r'[\n]'),(r'/\*',r'\*/')],
            'cc':     [('/(/)+',r'[\n]'),(r'/\*',r'\*/')],
            'cpp':    [('/(/)+',r'[\n]'),(r'/\*',r'\*/')],
            'h':      [('/(/)+',r'[\n]'),(r'/\*',r'\*/')],
            'hh':     [('/(/)+',r'[\n]'),(r'/\*',r'\*/')],
            'hpp':    [('/(/)+',r'[\n]'),(r'/\*',r'\*/')],
            'py':     [('#+',r'[\n]'),('\'\'\'',),('"""',)],
            'script': [('#+',r'[\n]')],
            'lua':    [(r'--\[\[',r'\]\]--')]
        }
    def __init__(self, mainsrc_path, wd):
        self.wd = wd
        self.mainsrc_path = os.abspath(mainsrc_path)
        
    def generate(self, src_path, srcipt_path=None):
        if script_path is None:
            script_path = src_path
        with open(script_path, 'r') as srcipt_file:
            ext = script_path.split('.')[-1]
            txt = script_file.read()
        #TODO
    
    @staticmethod
    def _parse(txt, ext):
        return TestCodeParser.parse('\n'.join(TestCodeGenerator._commented_lines(txt,ext)))
    
    @staticmethod
    def _commented_lines(txt, ext):
        comment_spans = list()
        for comment_style in TestCodeGenerator._comment_style_expr[ext]:
            if len(comment_style) == 2:
                # Match different start and end comments
                if comment_style[1] == r'[\n]':
                    # Match line comments
                    for begin_line in [0] + list(m.end() for m in re.finditer(comment_style[1], txt)):
                        m = re.search(comment_style[0], txt[begin_line:])
                        if m is not None:
                            end_line = begin_line + re.search(comment_style[1], txt[begin_line:]).start()
                            comment_spans.append((begin_line + m.end(), end_line))
                else:
                    # Match start/end comments
                    start_iter = re.finditer(comment_style[0], txt)
                    end_func = lambda i: i + re.search(comment_style[1],txt[i:]).start()
                    comment_spans.extend([(m.end(), end_func(m.end())) for m in start_iter])
            elif len(comment_style) == 1:
                # Match similar start and end comments
                start_iter = map(lambda m: m.end(), itertools.compress(re.finditer(comment_style[0], txt), itertools.cycle([True, False])))
                end_iter = map(lambda m: m.start(), itertools.compress(re.finditer(comment_style[0], txt), itertools.cycle([False, True])))
                comment_spans.extend(zip(start_iter, end_iter))
        for span in sorted(comment_spans, key=lambda s: s[0]):
            for line in txt[span[0]:span[1]].splitlines():
                yield line
    
    
