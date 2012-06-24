#!/usr/bin/env python

import os
import errno
import time


# Example for Unix or Mac OS X
shared_dir = os.environ['HOME'] + '/Dropbox/dropbox-buf'
local_dir = os.environ['HOME'] + '/dropbox-dl'

# Example for Windows
#shared_dir = r'C:\Documents and Settings\userid\My Documents\My Dropbox\dropbox-buf'
#local_dir = r'C:\Documents and Settings\userid\dropbox-dl'


def wait_appear(fname):
    while not os.path.exists(fname):
        time.sleep(1)


def mkdir_p(path, mode=None):
    try:
        os.makedirs(path)
    except OSError as ex:
        if ex.errno != errno.EEXIST:
            raise


def recv_file(dst_dir, filename, n_chunk):
    dst_name = dst_dir + '/' + filename

    if n_chunk == 1:
        src = shared_dir + '/.part_000'
        wait_appear(src)
        os.rename(src, dst_name)
    else:
        for n in xrange(n_chunk):
            part_name = '.part_%03d' % n
            src = shared_dir + '/' + part_name
            dst = local_dir + '/' + part_name
            wait_appear(src)
            os.rename(src, dst)

        with open(dst_name, 'wb') as f_merge:
            for n in xrange(n_chunk):
                part_file = local_dir + '/.part_%03d' % n
                with open(part_file, 'rb') as f_chunk:
                    f_merge.write(f_chunk.read())
                os.remove(part_file)

    print 'f:', os.path.normpath(dst_name)


def main():
    umask = os.umask(0)
    os.umask(umask)
    dir_mode = (~umask & 0777) | 0111
    mkdir_p(local_dir, dir_mode)
    cur_file = shared_dir + '/.cur'

    while True:
        wait_appear(cur_file)

        with open(cur_file) as f:
            ftype = f.readline()[:-1]
            if ftype == 'q':
                break
            else:
                dst_dir = (local_dir + '/' + f.readline()[:-1]).rstrip('/')

                if ftype == 'd':   # directory
                    mkdir_p(dst_dir, dir_mode)
                    print 'd:', os.path.normpath(dst_dir)
                elif ftype == 'f':   # file
                    filename = f.readline()[:-1]
                    n_chunk = int(f.readline())
                    mkdir_p(dst_dir, dir_mode)
                    recv_file(dst_dir, filename, n_chunk)

        os.remove(cur_file)

    os.remove(cur_file)


if __name__ == '__main__':
    main()
