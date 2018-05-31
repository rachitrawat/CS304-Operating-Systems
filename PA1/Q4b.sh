#!/bin/bash

awk '/ABC/{if( NR % 3 == 0 ) print}'  text.txt