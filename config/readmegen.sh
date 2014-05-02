#! /bin/bash

cd ".$1";
echo "# \`$1\`" >> README.md;
find * -not -name "*.pyc | *.md" -prune | sed "s/^/\\$(echo -e '\n\r')### /g" >> README.md;
cd $HOME;