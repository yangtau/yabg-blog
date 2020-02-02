#!/usr/bin/env python3
import sys


def update(filename):
    with open(filename) as f:
        lines = f.readlines()

    def replace(c):
        if c == '‘':
            return '「'
        elif c == '’':
            return '」'
        elif c == '“':
            return '『'
        elif c == '”':
            return '』'
        else:
            return c

    lines = [''.join(map(replace, l)) for l in lines]
    with open(filename, 'w') as f:
        f.writelines(lines)


if len(sys.argv) != 2:
    print('Usage: %s filename' % sys.argv[0])
    exit()

update(sys.argv[1])
