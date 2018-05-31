#!/bin/bash

if [ -f log ]; then
    rm log
fi

COUNTER=1000
         while [  "$COUNTER" -le "$((10**4))" ]; do
	 (time ./main.sh $COUNTER 5) >> log 2>&1 
	 ((COUNTER=COUNTER*10)) 
	 printf "\\n\\n" >> log 2>&1
         done

COUNTER=5
	 printf "\\n\\n" >> log 2>&1
         while [  "$COUNTER" -le "$((10**2))" ]; do
	 (time ./main.sh "$((10**4))" $COUNTER) >> log 2>&1 
	 ((COUNTER=COUNTER*2)) 
	 printf "\\n\\n" >> log 2>&1
         done




