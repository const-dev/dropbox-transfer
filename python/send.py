#!/usr/bin/env python3.2

import os
import sys
import time
import math


# Example for Unix or Mac OS X
shared_dir = os.environ['HOME'] + '/Dropbox/dropbox-buf'

# Example for Windows
#shared_dir = r'C:\Documents and Settings\userid\My Documents\My Dropbox\dropbox-buf'

chunk_size = 200 * 1024 * 1024   # 200 MB

cur_file = shared_dir + os.sep + '.cur'


def wait_disappear(fname):
    while os.path.exists(fname):
        time.sleep(1)


def split_file(fname, n_chunk):
    for n in range(n_chunk):
        tmp_file = shared_dir + os.sep + '.part_tmp'
        with open(fname, 'rb') as f_in, open(tmp_file, 'wb') as f_out:
            f_in.seek(n * chunk_size)
            f_out.write(f_in.read(chunk_size))
        part_file = shared_dir + os.sep + '.part_%03d' % n
        os.rename(tmp_file, part_file)
        wait_disappear(part_file)


# just being lazy and assume '/' works universally
def univ_path(path):
    if os.sep == '/':
        return path
    return '/'.join(path.split(os.sep))


def send_dir(dst_dir):
    print(time.strftime('%m/%d %H:%M:%S', time.gmtime()), end=' ')
    print('d:', os.path.normpath(dst_dir))
    with open(cur_file, 'w', encoding='utf-8') as f:
        f.write('d\n')   # directory
        f.write(univ_path(dst_dir) + '\n')
    wait_disappear(cur_file)


def send_file(src_path, dst_dir, fname):
    print(time.strftime('%m/%d %H:%M:%S', time.gmtime()), end=' ')
    print('f:', os.path.normpath(src_path))
    fsize = os.path.getsize(src_path)
    n_chunk = max(1, int(math.ceil(fsize / chunk_size)))

    with open(cur_file, 'w', encoding='utf-8') as f:
        f.write('f\n')   # file
        f.write(univ_path(dst_dir) + '\n')
        f.write(fname + '\n')
        f.write('%d\n' % n_chunk)

    split_file(src_path, n_chunk)
    wait_disappear(cur_file)


def main():
    for arg in sys.argv[1:]:
        if os.path.isfile(arg):
            send_file(arg, '', os.path.basename(arg))
        elif os.path.isdir(arg):
            rootdir = arg
            skip = len(rootdir)
            last_dir = ''
            dirs = [d for d in rootdir.split(os.sep) if d not in ['.', '']]
            if dirs and dirs[-1] != '..':
                last_dir = dirs[-1]
                send_dir(last_dir)

            for dirpath, dnames, fnames in os.walk(rootdir, followlinks=True):
                dirpath = dirpath.rstrip(os.sep)
                dst_dir = last_dir + os.sep + dirpath[skip:].lstrip(os.sep)
                dst_dir = dst_dir.rstrip(os.sep)   # for dirpath[skip:] == ''

                for dname in dnames:
                    send_dir(dst_dir + os.sep + dname)

                for fname in fnames:
                    send_file(dirpath + os.sep + fname, dst_dir, fname)

    print(time.strftime('%m/%d %H:%M:%S', time.gmtime()))
    with open(cur_file, 'w', encoding='utf-8') as f:
        f.write('q\n')   # quit


if __name__ == '__main__':
    main()
