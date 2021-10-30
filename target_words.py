import sys
import argparse
from collections import *
import numpy as np

def readConll(fh):
    eos = True
    for line in fh:
        if not line.strip() or line.startswith("#"):
            if not eos:
                yield (None, None, None, None)
                eos = True

            continue

        eos = False
        flds = line.split("\t")
        idn, word, lemma, uPos, aPos, posFeats = flds[0:6]
        yield (word, lemma, uPos, posFeats)

def findPossSyncretism(pos2form):
    sync = defaultdict(set)
    for pi, fi in pos2form.items():
        sync[fi.lower()].add(pi)

    return sync

def collapseSyncretism(lemmaPosForm):
    allPos = set()
    for lemma, pos2form in lemmaPosForm.items():
        for pos in pos2form:
            allPos.add(pos)

    syncsExcluded = defaultdict(Counter)

    for lemma, pos2form in lemmaPosForm.items():
        possSyncs = findPossSyncretism(pos2form)

        # for pi, fi in pos2form.items():
        #     print(pi, fi)

        # print()

        # for fi, syncset in possSyncs.items():
        #     print(fi, syncset)

        # print()

        for pi, fi in pos2form.items():
            syncset = possSyncs[fi]
            for pj in pos2form:
                if pj not in syncset:
                    #if pj not in syncsExcluded[pi]:
                    # if "Inf" in pj and "Tense=Pres" in pi and "Person=2" in pi:
                    #     print("pair", pos2form[pi], pos2form[pj], "excludes poss that",
                    #           pi, "and", pj, "are syncretic")

                    syncsExcluded[pi][pj] += 1
                    syncsExcluded[pj][pi] += 1

    cells = {}
    for pi in sorted(allPos, key=len):
        if pi not in cells:
            # print("finding all syncs for", pi)
            for pj in sorted(allPos, key=len):
                if syncsExcluded[pi][pj] < 5 and pj not in cells:
                    # print("adding sync between", pi, pj)
                    cells[pj] = pi


    # print("-----cell list-------")
    # for cell, cellname in cells.items():
    #     print(cell, "\t\t", cellname)

    return cells

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sample some target words from a corpus; write target files for SM2020 baseline.")
    parser.add_argument("--corpus", type=str,
                        help="UD corpus")
    parser.add_argument("--pos", type=str, default="VERB",
                        help="part of speech to target")
    parser.add_argument("--output", type=str, default=None,
                        help="Output file stem")
    parser.add_argument("--targets", default=100, type=int,
                        help="How many items to select")
    parser.add_argument("--skip", default=10, type=int,
                        help="How many most frequent items to skip")
    args = parser.parse_args()

    lCounts = Counter()
    lemmaPosForm = defaultdict(dict)
    with open(args.corpus) as fh:
        for (word, lemma, uPos, posFeats) in readConll(fh):
            if uPos == args.pos:
                lCounts[lemma] += 1

                if "Typo=Yes" in posFeats:
                    continue
                if "Abbr=Yes" in posFeats:
                    continue

                lemmaPosForm[lemma][posFeats] = word.lower()

    limited = {}
    for ind, (li, ct) in enumerate(lCounts.most_common(args.targets + args.skip)):
        if ind > args.skip:
            limited[li] = lemmaPosForm[li]

    cells = collapseSyncretism(limited)

    targetFileName = args.output + "." + args.pos + "-dev"
    with open(targetFileName, "w") as ofh:
        for ind, (li, ct) in enumerate(lCounts.most_common(args.targets + args.skip)):
            if ind > args.skip:
                # print(li, ct)
                ofh.write(li + "\n")

    rawFileName = args.output + ".txt"
    with open(rawFileName, "w") as ofh:
        with open(args.corpus) as fh:
            for (word, lemma, uPos, posFeats) in readConll(fh):
                if word is None:
                    ofh.write("\n")
                else:
                    ofh.write(word + " ")

    goldFileName = args.output + "." + args.pos + "-dev.gold"
    with open(goldFileName, "w") as ofh:
        for lemma, pos2form in limited.items():
            canonical = {}
            for pos, form in pos2form.items():
                canonical[cells[pos]] = form
                
            for pos, form in canonical.items():
                ofh.write("\t".join([lemma, form, pos]) + "\n")
