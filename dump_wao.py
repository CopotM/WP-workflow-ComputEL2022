import sys
import argparse
from collections import *
import numpy as np
import os
import json
from target_words import *

def readSentences(fh):
    curr = []
    for line in fh:
        words = line.strip().lower().split()
        for wi in words:
            curr.append(wi)
            if wi == ".":
                yield curr
                curr = []

def match(line, form):
    return form in line

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sample some target words from a corpus; write target files for SM2020 baseline.")
    parser.add_argument("--corpus", type=str,
                        help="Text corpus")
    parser.add_argument("--output", type=str, default=None,
                        help="Output file stem")
    parser.add_argument("--system", type=str, default=None,
                        help="System output file (clustering of lemma/form)")
    parser.add_argument("--examples", default=100, type=int,
                        help="Output n examples per word")
    args = parser.parse_args()
    if not args.output.endswith(".json"):
        args.output += ".json"

    if args.system:
        lemmaPosForm = defaultdict(dict)
        targets = set()
        with open(args.system) as fh:
            for line in fh:
                lemma, form, pos = line.strip().split()
                lemmaPosForm[lemma][pos] = form
                targets.add(form)
                targets.add(lemma)
        
    targets = list(set(targets))
                    
    with open(args.corpus) as fh:
        data = []
        for item in readSentences(fh):
            data.append(item)

    concordance = defaultdict(list)
    for ind, line in enumerate(data):
        for form in targets:
            if match(line, form) and len(concordance[form]) < args.examples:
                concordance[form].append(line)

    #reformat concordance to dictionary of { word : { word : word, examples : list } }
    res = {}
    for key, val in concordance.items():
        obj = { "word" : key, "examples" : val }
        res[key] = obj
                
    json.dump(res, open(args.output, "w"))
