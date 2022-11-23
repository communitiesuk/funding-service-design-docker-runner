#!/bin/sh

readarray array <<< $( cat repos.list )

cd ~/..

for element in ${array[@]}
do
    echo "clonning $element"
    git clone $element
done