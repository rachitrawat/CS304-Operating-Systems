#!/bin/bash

while true
do
    read -p "Email ID: " email
    echo
    if [[ "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$ ]]
    then
        echo "$email is a valid email ID."
        break
    else
        echo "$email is an invalid email ID."
    fi
done