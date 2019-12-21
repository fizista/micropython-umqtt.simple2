#!/usr/bin/env bash

OUTPUT=$(realpath ./build_port)

if [ -d "$OUTPUT" ]; then
    rm -r "$OUTPUT"
fi

mkdir "$OUTPUT"

function compile() {
    FILE_PATH="$1"

    file_name=$(basename $FILE_PATH)
    file_name="${file_name%.*}.mpy"
    file_dir=$(dirname $FILE_PATH)


    out_dir="${OUTPUT}/${file_dir}"
    out_path="$out_dir/$file_name"
    mp_path="${FILE_PATH%.*}.mpy"
    mp_path="${FILE_PATH:2}"

    if [ ! -d "$out_dir" ]; then
        mkdir "$out_dir"
    fi

    echo "Compile $FILE_PATH => $out_path"

    MP_FILE_PATH="${FILE_PATH%.*}.mpy"

    #mpy-cross -mno-unicode -o "$out_path" -s "$mp_path" "$FILE_PATH"
    #mpy-cross -march=xtensa -X emit=native "$FILE_PATH" &>/dev/null || mpy-cross -march=xtensa "$FILE_PATH"
    mpy-cross "$FILE_PATH"
    mv "$MP_FILE_PATH" "$out_dir"
}

cd ./src
for file_path in ./umqtt/*.py
do
    compile "$file_path"
done

cd ..
compile "./tests.py"
