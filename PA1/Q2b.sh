#!/bin/bash

sed -E ':A;s/\bapple/lemon\n/3;x;G;h;s/(.*)\n.*/\1/;x;s/.*\n//;/\bapple/bA;x;G;s/\n//g' FILE

#awk '{for(i=1; i<=NF; i++) if($i=="apple") if(++count%3==0) $i="lemon"}1' FILE