#!/bin/bash

mkdir -p cells
awk '{print>"cells/"$3"-cell.tsv"}' uzh.final
sed -e 's/\./\n\n/g' -e 's/^\([^ ]\)/ \1/g' ../../data/wao-multisyl/nt-ashless-sentences.txt | grep -v '^[[:space:]]*$' > clean.txt
pushd cells
for i in `ls -1`
do
    base_name=`echo $i|sed 's/-cell.tsv//'`
    for j in `cut -f2 $i`
    do grep " $j " ../clean.txt | head -n1 | sed "s/^\(.*\)$j\(.*\)$/ ,\"\1\",$j,True,\"\2\"/" >> $base_name-anno.csv
    done
done
popd
