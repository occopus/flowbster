#!/bin/sh

echo "Number of characters: `cat text | wc -m`" > stat
echo "Number of words: `cat text | wc -w`" >> stat
echo "Number of line: `cat text | wc -l`" >> stat

