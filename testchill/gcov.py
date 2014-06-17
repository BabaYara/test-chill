import functools
import itertools
import os
import os.path
import sys

from . import util

class GcovFile(object):
    def __init__(self, src_file_name, cov_file_path, lines, properties):
        self.src_file_name = src_file_name
        self.cov_file_path = cov_file_path
        self.lines = lines
        self.properties = properties
    
    @staticmethod
    def parse_file(gcov, fname, process=None):
        util.shell('gcov', [fname], wd=gcov.srcdir)
        cov_file_path = os.path.join(gcov.srcdir, fname + '.gcov')
        src_file_name = fname
        if os.path.exists(cov_file_path):
            with open(cov_file_path, 'r') as f:
                lines, properties = GcovFile.parse_lines(f.readlines(), process)
            return GcovFile(src_file_name, cov_file_path, lines, properties)
        else:
            return None
    
    @staticmethod
    def parse_lines(str_lines, process):
        properties = dict()
        lines = []
        for line in str_lines:
            pline = line.split(':')
            pline = list(map(str.strip, pline[0:2])) + pline[2:]
            if pline[1] == '0':
                properties[pline[2]] = pline[3].strip()
            elif pline[0][0] == '-':
                lines.append(GcovLine(int(pline[1]), dict(), ':'.join(pline[2:])))
            elif pline[0][0] == '#':
                lines.append(GcovLine(int(pline[1]), {process : 0}, ':'.join(pline[2:])))
            else:
                lines.append(GcovLine(int(pline[1]), {process : int(pline[0])}, ':'.join(pline[2:])))
        return lines, properties
    
    def merge(self, other):
        assert self.src_file_name == other.src_file_name
        GcovLine.merge_lines(self.lines, other.lines)
        self.properties.update(other.properties)


class GcovLine(object):
    def __init__(self, lineno, count_by_process, code):
        self.lineno = lineno
        self.count_by_process = count_by_process
        self.code = code
    
    @staticmethod
    def merge_lines(lines, other_lines):
        for line, other_line in zip(lines, other_lines):
            assert line.lineno == other_line.lineno
            assert line.code == other_line.code
            line.count_by_process.update(other_line.count_by_process)
    
    def count(self):
        runable_list = [l for l in self.count_by_process.values() if l is not None]
        if len(runable_list) == 0:
            return None
        else:
            return sum(runable_list)
    
    def __repr__(self):
        return str((self.lineno, self.count_by_process, self.code))


class Gcov(object):
    def __init__(self, srcdir):
        self.srcdir = srcdir
        self.files = dict()
    
    @staticmethod
    def parse(srcdir, process=None):
        gcov = Gcov(srcdir)
        gcov._append(filter(lambda f: f is not None, map(functools.partial(GcovFile.parse_file, gcov, process=process),
                util.filterext(['cc','c','cpp','h','hh'], os.listdir(srcdir)))))
        return gcov
    
    def _append(self, files):
        for f in files:
            if f.src_file_name in self.files:
                self.files[f.src_file_name].merge(f)
            else:
                self.files[f.src_file_name] = f
    
    def merge(self, other):
        self._append(other.files.values())


class GcovSet(object):
    def __init__(self):
        self.coverage_by_program = dict()
    
    def addprogram(self, prog_name, src_dir):
        self.coverage_by_program[prog_name] = Gcov(src_dir)
    
    def addcoverage(self, prog_name, process_name):
        cov = self.coverage_by_program[prog_name]
        cov.merge(Gcov.parse(cov.srcdir, process_name))
    
    def pretty_print(self, outfile=sys.stdout):
        pass
        
