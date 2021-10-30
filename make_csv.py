import sys
import argparse
from collections import *
import numpy as np
import os
import csv
from target_words import *

def writeExe(line, form, writer, goldWriter, negative=False):
    lineWords = [xx[0] for xx in line]
    index = lineWords.index(form)
    output = [" ".join(lineWords[:index]), lineWords[index], 
              str(not negative), " ".join(lineWords[index + 1:])]
    writer.writerow(output)
    (word, lemma, uPos, posFeats) = line[index]
    goldWriter.writerow([lemma, uPos])

def match(line, form):
    for (word, lemma, upos, posfeats) in line:
        if form == word:
            return True

def matchForms(line, forms):
    for (word, lemma, upos, posfeats) in line:
        if word in forms:
            return word

def writeCellExe(line, form, cells, writer, goldWriter, negative=False):
    lineWords = [xx[0] for xx in line]
    index = lineWords.index(form)
    output = [" ".join(lineWords[:index]), lineWords[index], 
              str(not negative), " ".join(lineWords[index + 1:])]
    writer.writerow(output)
    (word, lemma, uPos, posFeats) = line[index]
    goldWriter.writerow([uPos, posFeats, cells.get(posFeats, "None")])

def computeCanonCells(corpus, pos, skip, targets):
    lCounts = Counter()
    lemmaPosForm = defaultdict(dict)
    with open(corpus) as fh:
        for (word, lemma, uPos, posFeats) in readConll(fh):
            if uPos == pos:
                lCounts[lemma] += 1

                if "Typo=Yes" in posFeats:
                    continue
                if "Abbr=Yes" in posFeats:
                    continue

                lemmaPosForm[lemma][posFeats] = word.lower()

    limited = {}
    for ind, (li, ct) in enumerate(lCounts.most_common(targets + skip)):
        if ind > skip:
            limited[li] = lemmaPosForm[li]

    cells = collapseSyncretism(limited)
    return cells

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Make csv files for annotators.")
    parser.add_argument("--system", type=str,
                        help="System output file (clustering of lemma/form)")
    parser.add_argument("--corpus", type=str,
                        help="Corpus file in conll format")
    parser.add_argument("--n_lemma", type=int, default=10,
                        help="How many items to sample of each lemma")
    parser.add_argument("--n_cell", type=int, default=30,
                        help="How many items to sample of each cell")
    parser.add_argument("--output", type=str,
                        help="Output directory")
    parser.add_argument("--negative", action="store_true",
                        help="Add negative examples for cells")
    args = parser.parse_args()

    lemmaPosForm = defaultdict(dict)
    with open(args.system) as fh:
        for line in fh:
            lemma, form, pos = line.strip().split()
            lemmaPosForm[lemma][pos] = form

    with open(args.corpus) as fh:
        data = [[]]
        for item in readConll(fh):
            if item[0] is not None:
                data[-1].append(item)
            else:
                data.append([])

    os.makedirs(args.output + "/lemmas", exist_ok=True)
    os.makedirs(args.output + "/gold_lemmas", exist_ok=True)
    for lemma, pos2form in lemmaPosForm.items():
        with open(args.output + "/lemmas/%s.txt" % lemma, "w") as ofh:
            with open(args.output + "/gold_lemmas/%s.txt" % lemma, "w") as goldfh:
                writer = csv.writer(ofh)
                goldWriter = csv.writer(goldfh)

                for pos, form in pos2form.items():
                    nExe = 0
                    for ind, line in enumerate(data):
                        if match(line, form):
                            writeExe(line, form, writer, goldWriter)
                            nExe += 1

                        if nExe > args.n_lemma:
                            break

    cellForms = defaultdict(set)
    for lemma, pos2form in lemmaPosForm.items():
        for pos, form in pos2form.items():
            cellForms[pos].add(form)

    canonicalCells = computeCanonCells(args.corpus, "VERB", 10, 100)
    #print(canonicalCells)

    os.makedirs(args.output + "/cells", exist_ok=True)
    os.makedirs(args.output + "/gold_cells", exist_ok=True)
    for ind, (cell, forms) in enumerate(cellForms.items()):
        with open(args.output + "/cells/%d.txt" % ind, "w") as ofh:
            with open(args.output + "/gold_cells/%d.txt" % ind, "w") as goldfh:
                writer = csv.writer(ofh)
                goldWriter = csv.writer(goldfh)

                nExe = 0
                for ind, line in enumerate(data):
                    matched = matchForms(line, forms)
                    if matched:
                        writeCellExe(line, matched, canonicalCells, writer, goldWriter)
                        nExe += 1

                    if nExe > args.n_cell:
                        break

                if args.negative:
                    for otherCell, otherForms in cellForms.items():
                        if otherCell == cell:
                            continue

                        nExe = 0
                        for ind, line in enumerate(data):
                            matched = matchForms(line, otherForms)
                            if matched:
                                writeCellExe(line, matched, canonicalCells, writer, goldWriter,
                                             negative=True)
                                nExe += 1

                                #downsampled a bit arbitrarily
                                if nExe > args.n_cell / 6:
                                    break
