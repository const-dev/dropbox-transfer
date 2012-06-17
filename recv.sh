#!/bin/bash

local_dir="$HOME/dropbox-dl"
shared_dir="$HOME/Dropbox/dropbox-buf"

ftype="$shared_dir/type.txt"
dir_list="$shared_dir/dir-list.txt"
nfile="$shared_dir/n.txt"
name="$shared_dir/name.txt"

#verbose='-v'
verbose=''


function wait_appear {
    while [ ! -f "$1" ]; do
        sleep 1
    done
}

while true; do
    wait_appear "$ftype"
    f_type=`cat "$ftype"`
    rm $verbose -f "$ftype"

    if [ $f_type == q ]; then
        break
    elif [ $f_type == d ]; then
        wait_appear "$dir_list"
        cat "$dir_list" | while read d; do
            mkdir $verbose -p "$local_dir/$d"
        done
        rm -f "$dir_list"
    fi

    while true; do
        wait_appear "$nfile"
        if [ ! -s "$nfile" ]; then
            rm $verbose -f "$nfile"
            break
        fi
        n=`cat "$nfile"`
        rm $verbose -f "$nfile"

        for ((i = 1; i <= n; ++i)); do
            part_file=`printf "$shared_dir/part%03d" $i`
            wait_appear "$part_file"
            mv $verbose "$part_file" "$local_dir"
        done

        wait_appear "$name"
        eval cat "$local_dir/part*" > "$local_dir/`cat $name`"
        eval rm $verbose "$local_dir/part*"
        cat "$name"
        rm $verbose -f "$name"
    done
done
