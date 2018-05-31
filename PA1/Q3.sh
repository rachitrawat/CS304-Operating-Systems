#!/bin/bash

sent=$(cat keywords.txt | sed 's/\r$//' | tr '\n' ' ')
for word in $sent; do
   freq=$(tr ' ' '\n' < text.txt | grep "$word" | wc -l)
   echo "$word: $freq"
done