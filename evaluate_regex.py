import sys
import os
import csv
from collections import Counter
from target_words import *
from evaluate import *

def normalizeSpace(sent):
    return " ".join(sent.split())

def getGold(row, corpus):
    #sara's file has some malformed rows with an extra field
    mark, left, center, pred, right = row[:5]
    targetSent = left + center + right
    targetSent = normalizeSpace(targetSent)
    center = "".join([xx for xx in center if xx.isalpha()])
    for (sent, info) in corpus:
        if sent.startswith(targetSent):
            index = len(left.split())
            if left.strip() and not left.endswith(" "):
                index -= 1
            goldEntry = info[index]
            #can be a partial word match
            #print("verify", center, goldEntry[0])
            assert(center in goldEntry[0])
            return goldEntry

    assert(0), "Can't find %s" % targetSent

def scoreFile(fi, corpus, verbose):
    goldAnswers = []
    humanAnswers = []
    baselineAnswers = []

    with open(fi) as fh:
        reader = csv.reader(fh)
        for row in reader:
            goldWord, goldLemma, goldPos, goldFeats = getGold(row, corpus)
            goldAnswers.append((goldLemma, goldPos))
            mark, left, center, pred, right = row[:5]
            assert(pred == "False")
            pred = False
            baselineAnswers.append(pred)
            if mark.strip().lower() == "x":
                pred = True
            humanAnswers.append(pred)

    #print("gold answers:", goldAnswers)
    #print("human answers:", humanAnswers)

    humanInterp = bestInterpretation(humanAnswers, goldAnswers)
    humanScore = scoreInterpretation(humanInterp, humanAnswers, goldAnswers)

    if verbose:
        print("Best interpretation for human:", humanInterp)
        (tPos, tNeg, actual, nProp, total) = humanScore
        print("Human acc: %d/%d = %.3g" % (tPos + tNeg, total,
                                           (tPos + tNeg) / total))
        print("Human false pos %d false neg %d" % (nProp - tPos,
                                                   actual - tPos))
        print()

    return humanScore

def readCorpus(corpusFile):
    currSent = []
    currInfo = []
    res = [[currSent, currInfo]]

    with open(corpusFile) as fh:
        for (word, lemma, upos, feats) in readConll(fh):
            if word is not None:
                currSent.append(word)
                currInfo.append((word, lemma, upos, feats))

            else:
                currSent = []
                currInfo = []
                res.append([currSent, currInfo])

    res = [ [" ".join(sent), info] for (sent, info) in res]
    return res

def getGoldParadigm(targetLemma, corpus):
    paradigm = set()
    for (sent, info) in corpus:
        for (word, lemma, upos, feats) in info:
            if lemma == targetLemma:
                paradigm.add(word.strip().lower())

    return paradigm

def paradigmExpansion(fi, lemmaFi, goldParadigm, verbose):
    if verbose:
        print("Attested forms of lemma:", goldParadigm)

    known = set()
    base = set()

    with open(lemmaFi) as fh:
        reader = csv.reader(fh)
        for row in reader:
            mark, left, center, pred, right = row[:5]
            pred = eval(pred)
            if mark.strip():
                assert(mark.strip().lower() == "x")
                human = not pred
            else:
                human = pred

            if pred:
                base.add(center.lower().strip())

            if human:
                known.add(center.lower().strip())

    if verbose:
        print("Baseline paradigm:", base)
        print("Human-selected paradigm:", known)

    expanded = set(list(known))

    with open(fi) as fh:
        reader = csv.reader(fh)
        for row in reader:
            mark, left, center, pred, right = row[:5]
            pred = eval(pred)
            if mark.strip():
                assert(mark.strip().lower() == "x")
                human = not pred
            else:
                human = pred

            if human:
                expanded.add(center.lower().strip())

    if verbose:
        print("Additional forms:", expanded.difference(known))
        print("Additional correct forms:", expanded.intersection(goldParadigm).difference(known))
        print()

    return (len(expanded.difference(known)), 
            len(expanded.intersection(goldParadigm).difference(known)), 
            base,
            expanded)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Score regex search.")
    parser.add_argument("--regex", type=str,
                        help="Regex directory")
    parser.add_argument("--corpus", type=str,
                        help="Corpus file in conll format")
    parser.add_argument("--annot", type=str,
                        help="Annotation directory")
    parser.add_argument("--output_paradigms", type=str,
                        help="Where to put output paradigms")
    parser.add_argument("--verbose", type=int, default=0,
                        help="Annoy me with detailed output")
    args = parser.parse_args()

    corpus = readCorpus(args.corpus)

    directory = args.regex
    annotDirectory = args.annot

    dbase = os.path.basename(annotDirectory)
    lang, annotator = dbase.split("_")
    outParadigms = args.output_paradigms
    outGold = open(outParadigms + "/%s.gold" % lang, "w")
    outBase = open(outParadigms + "/%s.base" % lang, "w")
    outPred = open(outParadigms + "/%s_%s.pred" % (lang, annotator), "w")

    nExp = 0
    nCorrExp = 0
    scores = []
    print("Scoring directory", directory)
    for fi in os.listdir(directory):
        if fi.endswith(".csv"):
            print("Scoring file:", fi)
            with open(directory + "/" + fi) as fh:
                first = next(fh)
                if "no matches" in first:
                    print("Regex failed...\n")
                    continue

            score = scoreFile(directory + "/" + fi, corpus, args.verbose)
            scores.append(score)

            lemma = fi[:fi.index("_")]
            lemmaFile = annotDirectory + "/lemmas/" + lemma + ".txt"
            print("Scoring paradigm for lemma:", lemmaFile)
            goldParadigm = getGoldParadigm(lemma, corpus)
            exp, corrExp, baseParadigm, paradigm = paradigmExpansion(directory + "/" + fi, 
                                                                     lemmaFile, goldParadigm,
                                                                     args.verbose)
            nExp += exp
            nCorrExp += corrExp

            for item in goldParadigm:
                outGold.write(item + "\n")
            outGold.write("\n")

            for item in baseParadigm:
                outBase.write(item + "\n")
            outBase.write("\n")

            for item in paradigm:
                outPred.write(item + "\n")
            outPred.write("\n")

    outGold.close()
    outPred.close()
    hCorr, hMicroAcc, hMacroAcc = averageAcc(scores)
    
    print("----scores-------")
    print("Human micro-acc:", hMicroAcc, "macro:", hMacroAcc)
    print("Human contributed correct answers:", hCorr)
    print("New forms contributed to paradigms:", nExp)
    print("Correct forms contributed to paradigms:", nCorrExp)
    print("-----------------------\n")
