#!/bin/bash

lno=$(awk '{if( $0=NF % 2 == 0 && NR % 3 == 0) print NR}' text.txt)
for number in $lno; do
    sed -n "$number"p "text.txt"
done