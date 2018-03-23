#!/usr/bin/env python
'''
Condiment
---------

Conditionally include or remove code portion, according to the environment.
'''

__version__ = '0.6'

from os import environ, remove
from os.path import join, dirname, basename
from itertools import chain
from functools import partial
from copy import copy
from re import split
from codecs import open
from runpy import run_path
import datetime
import inspect
import ast
import sys
import imp
import re

is_py3 = sys.version >= '3'

if is_py3:
    from io import IOBase as file


class Iterator:
    def __init__(self, iterator):
        self.iterator = iterator

    def __iter__(self):
        return self

    def next(self):
        if is_py3:
            return self.iterator.__next__()
        else:
            return self.iterator.next()

    def push(self, value):
        self.iterator = chain([value], self.iterator)

    __next__ = next


class Parser(object):
    def __init__(self, prefix='WITH_', input=None, output=None):
        object.__init__(self)
        self.prefix = prefix
        self.eval_dict = {}
        self.output = output
        self.input = input
        self.output_name = None
        self.output_package = None

    def install(self):

        # ensure we are not installing ourself
        stack = inspect.stack()
        assert(len(stack) > 2)

        # check who is calling us, and ensure it's a python file
        frame = stack[2]
        filename = frame[1]
        self.output_name = frame[0].f_globals.get('__name__')
        self.output_package = frame[0].f_globals.get('__package__')
        assert(filename.endswith('.py'))
        self.input = filename

        # generate an output filename
        self.output = join(
            dirname(filename), '_ft_{}'.format(basename(filename))
        )

        self.do(run=True)

    def do(self, run=False):
        if imp.lock_held() is True:
            # inject global variables instead of rewriting the file
            self.do_inject()
        else:
            # just rewrite
            self.do_rewrite(run=run)

    @staticmethod
    def _fd_write(fd, encode, s):
        if encode:
            fd.write(s.encode('utf8'))
        else:
            fd.write(s)

    def do_rewrite(self, run=False):
        if self.output is sys.stdout:
            fd = self.output
            fd_write = partial(self._fd_write, fd, False)
        else:
            fd = open(self.output, 'wb')
            fd_write = partial(self._fd_write, fd, True)

        try:
            for index, line in self.parse(self.input):
                fd_write(line)

            now = datetime.datetime.now()
            fd_write('\n# ----- CONDIMENT VARIABLES -----\n')
            fd_write('# Generated at {}\n'
                     .format(now.strftime("%Y-%m-%d %H:%M")))
            for key, value in self.eval_dict.items():
                fd_write('# {} = {}\n'.format(key, value))
            fd_write('# ---------------------------------\n')
        finally:
            if self.output is not sys.stdout:
                fd.close()

        if run:
            self.on_the_fly()
            if self.output_name == '__main__':
                sys.exit(0)

    def do_inject(self):
        for index, line in self.parse(self.input):
            pass

        modname = self.output_name
        for key, value in self.eval_dict.items():
            setattr(sys.modules[modname], key, value)

    def on_the_fly(self):
        try:
            run_path(self.output)
        finally:
            if not isinstance(self.output, file):
                try:
                    remove(self.output)
                except Exception:
                    pass

    def parse(self, filename):
        r = re.compile(
            r"^[ \t\v]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)")

        if is_py3:
            encoding = 'utf8'
        else:
            encoding = 'ascii'

        with open(filename, 'rb', encoding, errors='ignore') as fd:
            for i in range(2):
                line = fd.readline()
                matches = r.findall(line)
                if matches:
                    encoding = matches[0]
                    break

        with open(filename, 'r', encoding=encoding) as fd:
            lines = fd.readlines()

        # share iterator accross all the states
        self.iterator = Iterator(enumerate(lines))
        for line in self._state_detect():
            yield line

    def _replace_defs(self, line):
        words = split('(\w+)', line)
        for key, value in self.eval_dict.items():
            for index, word in enumerate(words):
                if word == key:
                    words[index] = value
        return ''.join(words)

    def _state_detect(self):
        for index, line in self.iterator:
            sline = line.strip()
            if self._is_parsable_if(sline):

                if self._parse_if(sline):
                    for index, line in self._state_print_block(line):
                        yield index, line
                else:
                    self._state_strip_block(line)

            elif sline == '#exclude':
                self._read_exclude_block()

            else:
                yield index, self._replace_defs(line)

    def _read_exclude_block(self):
        for index, line in self.iterator:
            sline = line.strip()
            if sline == '#endexclude':
                break

    def _state_strip_block(self, line):
        block_start = self._get_block(line)
        for index, line in self.iterator:
            if not line.strip():
                continue
            block = self._get_block(line)
            if block <= block_start:
                self.iterator.push([index, line])
                break

    def _state_print_block(self, line):
        block_start = self._get_block(line)
        block_diff = None
        for index, line in self._state_detect():
            if not line.strip():
                continue
            block = self._get_block(line)
            if block_diff is None:
                block_diff = block - block_start
            if block_diff <= 0 or block <= block_start:
                self.iterator.push([index, line])
                break
            lline = line.lstrip()
            yield index, ' ' * (block - block_diff) + lline

    def _is_parsable_if(self, line):
        if line[:2] != 'if':
            return
        if line[-1] != ':':
            return
        if self.prefix not in line:
            return
        return True

    def _get_block(self, line):
        sline = line.lstrip()
        block = line[:len(line) - len(sline)]
        block = block.replace('\t', ' ' * 8)
        return len(block)

    def _parse_if(self, line):
        assert(line[:2] == 'if')
        assert(line[-1] == ':')
        prefix = self.prefix
        line = line[2:-1].strip()
        code = ast.parse(line)

        # gather only the name starting with the prefix
        for node in ast.walk(code):
            if type(node) is not ast.Name:
                continue
            if not node.id.startswith(prefix):
                continue
            self._define(node.id)

        # now evaluate
        return self._evaluate_if(line)

    def _evaluate_if(self, line):
        return bool(eval(line, copy(self.eval_dict)))

    def _define(self, key):
        if key not in self.eval_dict:
            self.eval_dict[key] = environ.get(key, '')


def install(**kwargs):
    Parser(**kwargs).install()


def run():
    import argparse
    parser = argparse.ArgumentParser(
        description='Activate features depending of the environment.')
    parser.add_argument(
        'input', metavar='source.py', nargs=1,
        help='Source file to process'
    )
    parser.add_argument(
        '-o', '--output', metavar='output', nargs='+',
        default=[sys.stdout],
        help='output file'
    )

    args = parser.parse_args()
    Parser(input=args.input[0], output=args.output[0]).do()


if __name__ == '__main__':
    run()
