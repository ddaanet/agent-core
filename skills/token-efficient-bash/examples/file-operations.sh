#!/usr/bin/env bash

exec 2>&1
set -xeuo pipefail

mkdir -p output/data output/logs
mv input/*.txt output/data/
ln -s ../output/data current
chmod 644 output/data/*.txt

if [[ -f output/data/config.txt ]]; then
    echo "Config file found"
fi

rm -f tmp/temp-*.log
