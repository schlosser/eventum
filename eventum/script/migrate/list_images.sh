#!/bin/bash

# iterate over the files
for file in $(find $1 -name '*.md'); do
    cat "$file" | ./print-images-from-md
done