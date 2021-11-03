import sys
import argparse
from collections import *
import numpy as np
import os
import csv
import re

def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = filename + " (" + str(counter) + ")" + extension
        counter += 1

    return path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="From regex, make annotator file containing matches.")
    #remove default before pushing
    parser.add_argument("--repository", type=str,
                        help="local path to git repository")
    parser.add_argument("--language", type=str,
                        help="english or croatian")
    parser.add_argument("--lexeme", type=str,
                        help="name of lemma file")
    parser.add_argument("--regex", type=str,
                        help="regex to look for in the corpus. In the form '(x)\\b'")
    parser.add_argument("--n_lemma", type=int, default=20,
                        help="How many items to sample")
    args = parser.parse_args()


    lemmaPosForm = defaultdict(dict)
    with open("".join([args.repository,"/baseline-out/",args.language.capitalize(),"/uzh.all"])) as fh:
        for line in fh:
            lemma, form, pos = line.strip().split()
            lemmaPosForm[lemma][pos] = form

rgex = re.compile(args.regex, re.IGNORECASE)
with open("".join([args.repository,"/data/",args.language.capitalize(),".txt"])) as fh:
        data = []
        for line in fh.readlines():
            m = re.search(rgex, line)
            if m:
                #if m.group(1) not in lexeme_forms:
                    s = line.split(m.group(1))
                    s.insert(1, m.group(1))
                    data.append(s)

for x in data:
    x.insert(0, "")
    x.insert(3, "False")

with open(uniquify("".join([args.repository,"/annotate/regex_output/",args.lexeme,"_",args.regex,".csv"])), "w", newline = "") as f:
    if data:
        writer = csv.writer(f)
        writer.writerows(data[0:args.n_lemma])
    else:
        f.write("no matches in the text, sorry!\n")
