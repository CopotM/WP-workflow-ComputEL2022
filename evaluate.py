import sys
import os
import csv
from collections import Counter

def bestInterpretation(proposed, gold):
    #what is the lemma most consistent with the proposed answers?

    #select only cases the annotator thinks are included in the category
    selectedGold = [gold[ind] for (ind, dec) in enumerate(proposed) if dec]
    #of these, select only verbs as potential interpretations
    selectedGold = [(lemma, pos) for (lemma, pos) in selectedGold
                    if pos == "VERB"]
    #of these, take the most common
    counts = Counter(selectedGold)
    if len(counts) == 0:
        return None
    else:
        return counts.most_common(1)[0][0]

def scoreInterpretation(interp, proposed, gold):
    def matches(xx, yy):
        try:
            return xx == yy or tuple(xx) == tuple(yy)
        except TypeError:
            return False
    
    tPos = 0
    tNeg = 0
    actual = 0
    nProp = 0

    for (prop, row) in zip(proposed, gold):

        if matches(row, interp) and interp is not None:
            actual += 1
            if prop:
                tPos += 1
        else:
            if not prop:
                tNeg += 1

        if prop:
            nProp += 1

    return tPos, tNeg, actual, nProp, len(gold)

def readAndValidate(fi, ref, verbose):
    marked = 0

    with open(ref) as fh:
        reader = csv.reader(fh)
        goldAnswers = list(reader)

    humanAnswers = []
    baselineAnswers = []

    try:
    
        with open(fi) as fh:
            reader = csv.reader(fh)
            for ind, (decision, left, item, system, right) in enumerate(reader):
                system = eval(system) #convert to bool
                baselineAnswers.append(system)

                if decision.strip():
                    assert(decision.strip().lower() == "x")
                    marked += 1
                    human = not system
                else:
                    human = system

                humanAnswers.append(human)

    except ValueError:
        print("Bad line:", ind)
        raise

    if verbose:
        print("Annotator changes:", marked)

    assert(len(humanAnswers) == len(goldAnswers))

    return marked, humanAnswers, baselineAnswers, goldAnswers
    
def scoreLemma(fi, ref, verbose=0):
    if verbose:
        print("Scoring lemma file:", fi)

    marked, humanAnswers, baselineAnswers, goldAnswers = readAndValidate(
        fi, ref, verbose)

    baseInterp = bestInterpretation(baselineAnswers, goldAnswers)    
    baseScore = scoreInterpretation(baseInterp, baselineAnswers, goldAnswers)
    
    if verbose:
        print("Best interpretation for baseline:", baseInterp)
        (tPos, tNeg, actual, nProp, total) = baseScore
        print("Baseline acc: %d/%d = %.3g" % (tPos + tNeg, total,
                                              (tPos + tNeg) / total))
        print("Baseline false pos %d false neg %d" % (nProp - tPos,
                                                      actual - tPos))

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

    return marked, baseScore, humanScore

def averageAcc(scores):
    accs = []
    corr = 0
    total = 0
    for (tpos, tneg, actual, nprop, localTot) in scores:
        acc = (tpos + tneg) / localTot
        accs.append(acc)
        corr += (tpos + tneg)
        total += localTot

    return corr, corr / total, sum(accs) / len(accs)

def bestCellInterpretation(proposed, gold):
    #what is the cell most consistent with the proposed answers?
    #this fn is the same as for lemmas, except that we decided to keep only
    #the syncretism category chosen for the paradigm cell
    selectedGold = [gold[ind] for (ind, dec) in enumerate(proposed) if dec]
    selectedGold = [syncFeats for (pos, feats, syncFeats) in selectedGold
                    if pos == "VERB"]
    counts = Counter(selectedGold)
    if len(counts) == 0:
        return None
    else:
        return counts.most_common(1)[0][0]

def scoreCell(fi, ref, verbose=0):
    if verbose:
        print("Scoring cell file:", fi)

    try:
        marked, humanAnswers, baselineAnswers, goldAnswers = readAndValidate(
            fi, ref, verbose)
    except ValueError:
        print("Problems with format of", fi)
        raise

    goldSync = [syncFeats for (pos, feats, syncFeats) in goldAnswers]
    
    baseInterp = bestCellInterpretation(baselineAnswers, goldAnswers)
    baseScore = scoreInterpretation(baseInterp, baselineAnswers, goldSync)
    
    if verbose:
        print("Best interpretation for baseline:", baseInterp)
        (tPos, tNeg, actual, nProp, total) = baseScore
        print("Baseline acc: %d/%d = %.3g" % (tPos + tNeg, total,
                                              (tPos + tNeg) / total))
        print("Baseline false pos %d false neg %d" % (nProp - tPos,
                                                      actual - tPos))

    humanInterp = bestCellInterpretation(humanAnswers, goldAnswers)
    humanScore = scoreInterpretation(humanInterp, humanAnswers, goldSync)

    if verbose:
        print("Best interpretation for human:", humanInterp)
        (tPos, tNeg, actual, nProp, total) = humanScore
        print("Human acc: %d/%d = %.3g" % (tPos + tNeg, total,
                                           (tPos + tNeg) / total))
        print("Human false pos %d false neg %d" % (nProp - tPos,
                                                   actual - tPos))
        print()
        
    return marked, baseScore, humanScore
    
def scoreLemmas(directory, verbose):
    gold = directory + "/gold_lemmas"
    annot = directory + "/lemmas"

    totalMarked = 0
    baseScores = []
    humanScores = []
    
    for fi in os.listdir(annot):
        if not fi.endswith(".txt"):
            continue

        (marked, baseScore, humanScore) = scoreLemma(
            annot + "/" + fi, gold + "/" + fi, verbose)
        totalMarked += marked
        baseScores.append(baseScore)
        humanScores.append(humanScore)

    bCorr, bMicroAcc, bMacroAcc = averageAcc(baseScores)
    hCorr, hMicroAcc, hMacroAcc = averageAcc(humanScores)
    
    print("----lemma scores-------")
    print("Human annotator marked:", totalMarked)
    print("Baseline micro-acc:", bMicroAcc, "macro:", bMacroAcc)
    print("Human micro-acc:", hMicroAcc, "macro:", hMacroAcc)
    print("Human contributed correct answers:", hCorr - bCorr)
    print("-----------------------\n")

def scoreCells(directory, verbose):
    gold = directory + "/gold_cells"
    annot = directory + "/cells"

    totalMarked = 0
    baseScores = []
    humanScores = []
    
    for fi in os.listdir(annot):
        if not fi.endswith(".txt"):
            continue

        (marked, baseScore, humanScore) = scoreCell(
            annot + "/" + fi, gold + "/" + fi, verbose)

        totalMarked += marked
        baseScores.append(baseScore)
        humanScores.append(humanScore)

    bCorr, bMicroAcc, bMacroAcc = averageAcc(baseScores)
    hCorr, hMicroAcc, hMacroAcc = averageAcc(humanScores)
    
    print("----cell scores-------")
    print("Human annotator marked:", totalMarked)
    print("Baseline micro-acc:", bMicroAcc, "macro:", bMacroAcc)
    print("Human micro-acc:", hMicroAcc, "macro:", hMacroAcc)
    print("Human contributed correct answers:", hCorr - bCorr)
    print("-----------------------\n")

if __name__ == "__main__":
    directory = sys.argv[1]
    verbose = 0
    if len(sys.argv) > 2:
        verbose = int(sys.argv[2])

    print("Scoring directory", directory)

    scoreLemmas(directory, verbose)
    scoreCells(directory, verbose)
