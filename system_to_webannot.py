import sys
import argparse
from collections import *

def readSystem(sysFile):
    lexemes = {}
    cells = {}
    with open(sysFile) as fh:
        for line in fh:
            (lemma, form, cell) = line.strip().split("\t")

            #we should support spaces in tokens, it's conceptually useful
            #but makes it more difficult to scan for annotatable spans in
            #the corpus--- will not bother for now
            if " " in form:
                continue

            lexemes[form] = lemma
            cells[form] = cell
            
    return lexemes, cells

def readCorpus(corFile):
    with open(corFile) as fh:
        return list([xx.split() for xx in fh])

def annotateRel(corpus, lexemes, cells):
    """Each element of the corpus is linked to the most recent
    previous occurrence of its lexeme and of its cell."""
    lexLinks = []
    cellLinks = []
    mostRecentLemma = {}
    mostRecentCell = {}

    for ind, si in enumerate(corpus):
        currLex = []
        lexLinks.append(currLex)
        currCell = []
        cellLinks.append(currCell)

        for wInd, wj in enumerate(si):
            wjLex = lexemes.get(wj, None)
            wjCell = cells.get(wj, None)

            mostRecLex, recLexCell = mostRecentLemma.get(wjLex, (None, None))
            mostRecCell, recCellLex = mostRecentCell.get(wjCell, (None, None))

            if recLexCell == wjCell:
                #if the most recent lexeme-mate had the same cell too, record a full match
                currLex.append((mostRecLex, "same"))
            else:
                currLex.append((mostRecLex, "lex"))

            if recCellLex == wjLex:
                currCell.append((mostRecCell, "same"))
            else:
                currCell.append((mostRecCell, "cell"))

            if wj in lexemes:
                if wjLex not in mostRecentLemma:
                    #mark chain beginnings so we get a markable annotation on link targets
                    currLex[-1] = (True, True)

                #remember this word as potential link target and record what cell it belonged to
                mostRecentLemma[lexemes[wj]] = ((ind, wInd), wjCell)

            if wj in cells:
                if wjCell not in mostRecentCell:
                    currCell[-1] = (True, True)

                mostRecentCell[cells[wj]] = ((ind, wInd), wjLex)

    return lexLinks, cellLinks

def annotateChain(corpus, lexemes, cells):
    """Each element is linked to its chain and sequence number."""
    lexLinks = []
    cellLinks = []
    lemmaSeq = Counter()
    cellSeq = Counter()
    chainTab = {}

    for ind, si in enumerate(corpus):
        #print("!!!", si)
        currLex = []
        lexLinks.append(currLex)
        currCell = []
        cellLinks.append(currCell)

        for wInd, wj in enumerate(si):
            if wj in lexemes:
                #print("markable lex", wj, "belongs to", lexemes[wj])
                
                chain = chainTab.get(lexemes[wj], len(chainTab) + 1)
                chainTab[lexemes[wj]] = chain
                lemmaSeq[lexemes[wj]] += 1
                seq = lemmaSeq[lexemes[wj]]
                currLex.append((chain, seq))
            else:
                currLex.append(None)

            if wj in cells:
                chain = chainTab.get(cells[wj], len(chainTab) + 1)
                chainTab[cells[wj]] = chain
                cellSeq[cells[wj]] += 1
                seq = cellSeq[cells[wj]]
                currCell.append((chain, seq))
            else:
                currCell.append(None)

    return lexLinks, cellLinks

def debugOutput(corpus, lexLinks, cellLinks):
    for line, lex, cell in zip(subsection, lexLinks, cellLinks):
        for (ti, li, ci) in zip(line, lex, cell):
            if li is not None or ci is not None:
                print(ti, li, ci, end="  ")
            else:
                print(ti, end=" ")
        print()

def tsvOutputChain(corpus, lexLinks, cellLinks, output):
    with open(output, "w") as ofh:
        ofh.write("#FORMAT=WebAnno TSV 3.3\n")
        ofh.write("#T_CH=webanno.custom.CellLink|referenceRelation|referenceType\n")
        ofh.write("#T_CH=webanno.custom.LexemeLink|referenceRelation|referenceType\n")
        ofh.write("\n")
        
        chInd = 0
        for ind, (line, lex, cell) in enumerate(zip(corpus, lexLinks, cellLinks)):
            ofh.write("\n")
            ofh.write("#Text={0}\n".format(" ".join(line)))

            for wInd, (ti, li, ci) in enumerate(zip(line, lex, cell)):
                index = "{0}-{1}".format(ind + 1, wInd + 1)
                charIndex = "{0}-{1}".format(chInd, chInd + len(ti))
                chInd += len(ti) + 1
                if li != None:
                    chain, seq = li
                    lexChain1 = "*[{0}]".format(chain)
                    lexChain = "*->{0}-{1}".format(chain, seq)
                else:
                    lexChain1 = "_"
                    lexChain = "_"

                if ci != None:
                    chain, seq = ci
                    cellChain1 = "*[{0}]".format(chain)
                    cellChain = "*->{0}-{1}".format(chain, seq)
                else:
                    cellChain1 = "_"
                    cellChain = "_"

                ofh.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t\n".format(index, charIndex, ti,
                                                                       cellChain, cellChain1,
                                                                       lexChain, lexChain1))

def tsvOutputRel(corpus, lexLinks, cellLinks, output):
    with open(output, "w") as ofh:
        ofh.write("#FORMAT=WebAnno TSV 3.3\n")
        ofh.write("#T_SP=de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.SurfaceForm|value\n")
        ofh.write("#T_RL=webanno.custom.Lex_r|morph|BT_de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.SurfaceForm\n")
        ofh.write("\n")

        chInd = 0
        for ind, (line, lex, cell) in enumerate(zip(corpus, lexLinks, cellLinks)):
            ofh.write("\n")
            ofh.write("#Text={0}\n".format(" ".join(line)))

            for wInd, (ti, li, ci) in enumerate(zip(line, lex, cell)):
                index = "{0}-{1}".format(ind + 1, wInd + 1)
                charIndex = "{0}-{1}".format(chInd, chInd + len(ti))
                markable = "_"
                chInd += len(ti) + 1

                if li[0] != None:
                    markable = "*"
                    if li[0] is not True:
                        lineNum, wordNum = li[0]
                        lexAssoc = "{0}-{1}".format(lineNum + 1, wordNum + 1)
                        liType = li[1]
                else:
                    lexAssoc = None

                if ci[0] != None:
                    markable = "*"
                    if ci[0] is not True:
                        lineNum, wordNum = ci[0]
                        cellAssoc = "{0}-{1}".format(lineNum + 1, wordNum + 1)
                        ciType = ci[1]
                else:
                    cellAssoc = None
                    
                if lexAssoc and cellAssoc:
                    if lexAssoc == cellAssoc:
                        #single link: predecessor is identical form
                        assoc = lexAssoc
                        feat = "same"
                    else:
                        #multilink
                        assoc = cellAssoc + "|" + lexAssoc
                        feat = ciType + "|" + liType
                elif lexAssoc:
                    assoc = lexAssoc
                    feat = liType
                elif cellAssoc:
                    assoc = cellAssoc
                    feat = ciType
                else:
                    assoc = "_"
                    feat = "_"
                    
                ofh.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t\n".format(index, charIndex, ti,
                                                                    markable, feat, assoc))

        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Turn SigMorphon 2020 shared task into WebAnnot.")
    parser.add_argument("--corpus", type=str,
                        help="Unannotated text corpus (the bible file).")
    parser.add_argument("--system", type=str,
                        help="System analysis (the output file).")
    parser.add_argument("--begin", type=int, default=0,
                        help="Line number of the corpus to begin at.")
    parser.add_argument("--end", type=int, default=None,
                        help="Line number of the corpus to end at.")
    parser.add_argument("--output", type=str, default=None,
                        help="Output file name (default input+.webannot)")
    parser.add_argument("--output_type", type=str, default="chain",
                        help="How to output (chain/relation).")
    args = parser.parse_args()

    if args.output is None:
        args.output = args.system + ".webannot"

    lexemes, cells = readSystem(args.system)

    corpus = readCorpus(args.corpus)
    
    if args.end == None:
        args.end = len(corpus)

    if args.end - args.begin <= 0:
        print("End must be after begin.")

    subsection = corpus[args.begin : args.end]

    if args.output_type == "chain":
        lexLinks, cellLinks = annotateChain(subsection, lexemes, cells)
        #debugOutput(subsection, lexLinks, cellLinks)
        tsvOutputChain(subsection, lexLinks, cellLinks, args.output)
    elif args.output_type == "relation":
        lexLinks, cellLinks = annotateRel(subsection, lexemes, cells)
        #debugOutput(subsection, lexLinks, cellLinks)
        tsvOutputRel(subsection, lexLinks, cellLinks, args.output)        
    else:
        print("Output type", args.output_type, "not supported yet.")
        sys.exit(1)
