#!/bin/bash

mkdir -p lexemes
awk '{print>"lexemes/"$1"-lexeme.tsv"}' uzh.final
sed -e 's/\./\n\n/g' -e 's/^\([^ ]\)/ \1/g' ../../data/wao-multisyl/nt-ashless-sentences.txt | grep -v '^[[:space:]]*$' > clean.txt
cd lexemes
for i in `ls -1`
do
    base_name=`echo $i|sed 's/-lexeme.tsv//'`
    for j in `cut -f2 $i`
    do grep " $j " ../clean.txt | head -n1 | sed "s/^\(.*\)$j\(.*\)$/ ,\"\1\",$j,True,\"\2\"/" >> $base_name-anno.csv
    done
done
