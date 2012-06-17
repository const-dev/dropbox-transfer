#!/bin/bash

shared_dir="$HOME/Dropbox/dropbox-buf"

ftype="$shared_dir/type.txt"
dir_list="$shared_dir/dir-list.txt"
nfile="$shared_dir/n.txt"
name="$shared_dir/name.txt"

sp_size=204800


function wait_disapper {
    while [ -f "$1" ]; do
        sleep 1
    done
}

while (( "$#" )); do 
    src="$1"
    shift

    if [ -d "$src" ]; then
        echo d > "$ftype"
        find -L "$src" -type d | python trim_path.py "$src" > "$dir_list"
    else
        echo f > "$ftype"
    fi

    find -L "$src" -type f | while read f; do
        echo "$f"
        n=`ls -Hs "$f" | cut -d ' ' -f 1 | python n_split.py $sp_size`
        echo $n > "$nfile"

        if [ -d "$src" ]; then
            echo $f | python trim_path.py "$src" > "$name"
        else
            basename "$src" > "$name"
        fi

        for ((i = 1; i <= n; ++i)); do
            part_name=`printf "$shared_dir/part%03d" $i`
            echo $part_name
            echo "split -n $i/$n $f > $part_name"
            split -n $i/$n "$f" > "$part_name"
            wait_disapper "$part_name"
        done

        wait_disapper "$name"
    done

    touch "$nfile"
done

echo q > "$ftype"
