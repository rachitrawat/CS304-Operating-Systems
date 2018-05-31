#!/bin/bash

calc_min_max () {
array=("$@")
max=${array[0]}
min=${array[0]}

      for i in "${array[@]}"; do
  	(( i > max )) && max=$i
  	(( i < min )) && min=$i
	done

echo "$max" >> max_min
echo "$min" >> max_min
}


if [ -f random ]; then
    rm random
fi

if [ -f max_min ]; then
    rm max_min
fi

N=$1
P=$2

echo "N : " $N
echo "P : " $P

 COUNTER=1
         while [  $COUNTER -le "$N" ]; do

	shuf -i 0-$((10**7)) -n 1 >> random
             ((COUNTER=COUNTER+1)) 
         done



mapfile -t array < random

arraylength=${#array[@]}
declare -a arr
count=1
pr_count=0

for (( i=1; i<arraylength+1; i++ ));
do
	arr+=("${array[$i-1]}")
	 if [ $count -eq $((N / P)) ]; then
		pr_count=$((pr_count + 1))
		calc_min_max "${arr[@]}" & 
		arr=()
		count=0

	fi

count=$((count + 1))
done

wait
mapfile -t arr_max_min < max_min
calc_min_max "${arr_max_min[@]}" & 
wait
