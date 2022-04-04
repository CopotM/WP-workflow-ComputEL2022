import sys
import argparse
from collections import *
import numpy as np
import os
import json
from target_words import *

def match(line, form):
    for (word, lemma, upos, posfeats) in line:
        if form == word.lower():
            return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sample some target words from a corpus; write target files for SM2020 baseline.")
    parser.add_argument("--corpus", type=str,
                        help="UD corpus")
    parser.add_argument("--system", type=str, default=None,
                        help="System output file (clustering of lemma/form)")
    parser.add_argument("--pos", type=str, default=None,
                        help="part of speech to target")
    parser.add_argument("--output", type=str, default=None,
                        help="Output file stem")
    parser.add_argument("--targets", default=100, type=int,
                        help="How many items to select")
    parser.add_argument("--skip", default=10, type=int,
                        help="How many most frequent items to skip")
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
                
    else:    
        lCounts = Counter()
        lemmaPosForm = defaultdict(dict)
        with open(args.corpus) as fh:
            for (word, lemma, uPos, posFeats) in readConll(fh):
                if word and word.isalpha():
                    if args.pos is None or uPos == args.pos:
                        if args.pos is not None:
                            lCounts[lemma] += 1
                        else:
                            lCounts[word.lower()] += 1

                        if "Typo=Yes" in posFeats:
                            continue
                        if "Abbr=Yes" in posFeats:
                            continue

                        lemmaPosForm[lemma][posFeats] = word.lower()
                        
        targets = []
        for ind, (li, ct) in enumerate(lCounts.most_common(
                args.targets + args.skip)):
            if ind > args.skip:
                if args.pos is None:
                    targets.append(li)
                else:
                    for pos, form in lemmaPosForm[li].items():
                        targets.append(form)

    targets = list(set(targets))
                    
    with open(args.corpus) as fh:
        data = [[]]
        for item in readConll(fh):
            if item[0] is not None:
                data[-1].append(item)
            else:
                data.append([])

    concordance = defaultdict(list)
    for ind, line in enumerate(data):
        for form in targets:
            if match(line, form) and len(concordance[form]) < args.examples:
                words = [xx[0] for xx in line]
                concordance[form].append(words)

    #reformat concordance to dictionary of { word : { word : word, examples : list } }
    res = {}
    for key, val in concordance.items():
        obj = { "word" : key, "examples" : val }
        res[key] = obj
                
    json.dump(res, open(args.output, "w"))
