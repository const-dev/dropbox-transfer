#!/usr/bin/env python

from __future__ import division
import os
import errno
import sys
import time


#shared_dir = os.environ['HOME'] + '/Dropbox/dropbox-buf'
shared_dir = '/tmp/dropbox-buf'
#local_dir = os.environ['HOME'] + '/dropbox-dl'
local_dir = '/tmp/dropbox-dl'


def wait_appear(fname):
    while not os.path.exists(fname):
        time.sleep(1)


def mkdir_p(path, mode=None):
    try:
        os.makedirs(path)
    except OSError as ex:
        if ex.errno == errno.EEXIST:
            pass
        else:
            raise


def recv_file(dirname, filename, n_chunk):
    for n in xrange(n_chunk):
        part_name = '.part_%03d' % n
        src = shared_dir + '/' + part_name
        dst = local_dir + '/' + part_name
        wait_appear(src)
        os.rename(src, dst)

    with open(dirname + '/' + filename, 'wb') as f_merge:
        for n in xrange(n_chunk):
            part_file = local_dir + '/.part_%03d' % n
            with open(part_file, 'rb') as f_chunk:
                f_merge.write(f_chunk.read())
            os.remove(part_file)

    print dirname + '/' + filename


def main():
    umask = os.umask(0)
    os.umask(umask)
    dir_mode = (~umask & 0777) | 0111

    cur_file = shared_dir + '/.cur'

    while True:
        wait_appear(cur_file)

        with open(cur_file) as f:
            ftype = f.readline()[:-1]
            if ftype == 'q':
                os.remove(cur_file)
                break
            else:
                dirname = f.readline()[:-1]
                if ftype == 'd':   # directory
                    mkdir_p(dirname, dir_mode)
                elif ftype == 'f':   # file
                    filename = f.readline()[:-1]
                    n_chunk = int(f.readline())
                    local_path = local_dir + '/' + dirname
                    mkdir_p(local_path, dir_mode)
                    recv_file(local_path, filename, n_chunk)

        os.remove(cur_file)


if __name__ == '__main__':
    main()
