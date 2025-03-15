#!/bin/bash

for day in {01..31}; do                                                                                  
  for month in {01..12}; do
    password="rgiskard$day$month"
    echo -n "$password" | md5sum | awk '{print $1}'
  done
done > md5_wordlist.txt
