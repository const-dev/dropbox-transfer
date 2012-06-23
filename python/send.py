#!/usr/bin/env python

from __future__ import division
import os
import sys
import time
import math


chunk_size = 200 * 1024 * 1024   # 200 MB

shared_dir = os.environ['HOME'] + '/Dropbox/dropbox-buf'
#shared_dir = '/tmp/dropbox-buf'

cur_file = shared_dir + '/.cur'


def wait_disappear(fname):
    while os.path.exists(fname):
        time.sleep(1)


def split_file(fname, n_chunk):
    for n in xrange(n_chunk):
        part_file = shared_dir + '/.part_%03d' % n
        with open(fname, 'rb') as f_in, open(part_file, 'wb') as f_out:
            f_in.seek(n * chunk_size)
            f_out.write(f_in.read(chunk_size))
        if n < n_chunk - 1:
            wait_disappear(part_file)


def send_dir(dst_dir):
    with open(cur_file, 'w') as f:
        f.write('d\n')
        f.write(dst_dir + '\n')
    wait_disappear(cur_file)


def send_file(src_path, dst_dir, fname):
    fsize = os.path.getsize(src_path)
    n_chunk = max(1, int(math.ceil(fsize / chunk_size)))

    with open(cur_file, 'w') as f:
        f.write('f\n')
        f.write(dst_dir + '\n')
        f.write(fname + '\n')
        f.write('%d\n' % n_chunk)

    split_file(src_path, n_chunk)
    wait_disappear(cur_file)


def main():
    for arg in sys.argv[1:]:
        if os.path.isfile(arg):
            print 'file:', arg
            send_file(arg, '', os.path.basename(arg))
        elif os.path.isdir(arg):
            rootdir = arg
            skip = len(rootdir)
            last_dir = ''
            dirs = [d for d in rootdir.split('/') if d not in ['.', '']]
            if dirs and dirs[-1] != '..':
                last_dir = dirs[-1] + '/'
                send_dir(last_dir)

            for dirpath, dnames, fnames in os.walk(rootdir, followlinks=True):
                dirpath = dirpath.rstrip('/')
                dst_dir = (last_dir + dirpath[skip:].lstrip('/')).rstrip('/')

                for dname in dnames:
                    print 'dir:', dirpath + '/' + dname
                    send_dir(dst_dir + '/' + dname)

                for fname in fnames:
                    src_path = dirpath + '/' + fname
                    print 'file:', src_path
                    send_file(src_path, dst_dir, fname)

    with open(cur_file, 'w') as f:
        f.write('q\n')


if __name__ == '__main__':
    main()
