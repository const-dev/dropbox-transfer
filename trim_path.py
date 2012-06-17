#!/usr/bin/env python

import sys

path = sys.argv[1]
skip = len(sys.argv[1])
prefix = ''
dir_names = [d for d in path.split('/') if d not in ['.', '']]
if dir_names:
    if dir_names[-1] != '..':
        prefix = dir_names[-1] + '/'

for line in sys.stdin:
    dname = prefix + line[skip:].rstrip().lstrip('/')
    if dname != '':
        print dname

