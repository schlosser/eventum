#!/bin/bash

# iterate over the files
for file in $(find $1 -name '*.html'); do
    echo "---------"
    echo "$file"
    filename="$(basename $file)"
    md=".md"
    out="$2"/${filename/\.html/.md}
    echo "$out"
    cat "$file" | ./post-to-content | ./html-to-md > "$out"
done