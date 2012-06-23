#!/usr/bin/env python

from __future__ import division
import os
import errno
import sys
import time
import math


chunk_size = 200 * 1024 * 1024   # 200 MB

#shared_dir = os.environ['HOME'] + '/Dropbox/dropbox-buf'
shared_dir = '/tmp/dropbox-buf'


def wait_disappear(fname):
    while os.path.exists(fname):
        time.sleep(1)


def send_file(fname, n_chunk):
    for n in xrange(n_chunk):
        part_file = shared_dir + '/.part_%03d' % n
        with open(fname, 'rb') as f_in, open(part_file, 'wb') as f_out:
            f_in.seek(n * chunk_size)
            f_out.write(f_in.read(chunk_size))
        if n < n_chunk - 1:
            wait_disappear(part_file)


def main():
    rootdir = sys.argv[1]
    skip = len(rootdir)
    last_dir = ''
    dirs = [d for d in rootdir.split('/') if d not in ['.', '']]
    if dirs and dirs[-1] != '..':
        last_dir = dirs[-1] + '/'

    cur_file = shared_dir + '/.cur'

    for dirpath, dirnames, filenames in os.walk(rootdir, followlinks=True):
        path = (last_dir + dirpath[skip:].lstrip('/')).rstrip('/')

        for dname in dirnames:
            print 'dir:', path + '/' + dname
            with open(cur_file, 'w') as f:
                f.write('d\n')
                f.write(path + '/' + dname + '\n')
            wait_disappear(cur_file)

        for fname in filenames:
            print 'file:', path + '/' + fname

            filepath = dirpath + '/' + fname
            fsize = os.path.getsize(filepath)
            n_chunk = max(1, int(math.ceil(fsize / chunk_size)))

            with open(cur_file, 'w') as f:
                f.write('f\n')
                f.write(path + '\n')
                f.write(fname + '\n')
                f.write('%d\n' % n_chunk)

            send_file(filepath, n_chunk)
            wait_disappear(cur_file)

    with open(cur_file, 'w') as f:
        f.write('q\n')


if __name__ == '__main__':
    main()
