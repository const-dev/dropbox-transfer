#!/usr/bin/env python3.2

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
    dst = dst_dir + '/' + filename

    if n_chunk == 1:
        src = shared_dir + '/.part_000'
        wait_appear(src)
        os.rename(src, dst)
    else:
        dst_part = dst + '.part'

        try:
            os.remove(dst_part)
        except OSError as ex:
            if ex.errno != errno.ENOENT:
                raise

        for n in range(n_chunk):
            src = shared_dir + '/.part_%03d' % n
            wait_appear(src)
            with open(src, 'rb') as f_chunk, open(dst_part, 'ab') as f_merge:
                f_merge.write(f_chunk.read())
            os.remove(src)
        os.rename(dst_part, dst)

    print('f:', os.path.normpath(dst))


def main():
    umask = os.umask(0)
    os.umask(umask)
    dir_mode = (~umask & 0o777) | 0o111
    mkdir_p(local_dir, dir_mode)
    cur_file = shared_dir + '/.cur'

    while True:
        wait_appear(cur_file)

        with open(cur_file, 'r', encoding='utf-8') as f:
            ftype = f.readline()[:-1]
            if ftype == 'q':
                break
            else:
                dst_dir = (local_dir + '/' + f.readline()[:-1]).rstrip('/')

                if ftype == 'd':   # directory
                    mkdir_p(dst_dir, dir_mode)
                    print('d:', os.path.normpath(dst_dir))
                elif ftype == 'f':   # file
                    filename = f.readline()[:-1]
                    n_chunk = int(f.readline())
                    mkdir_p(dst_dir, dir_mode)
                    recv_file(dst_dir, filename, n_chunk)

        os.remove(cur_file)

    os.remove(cur_file)


if __name__ == '__main__':
    main()
