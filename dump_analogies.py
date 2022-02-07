import sys
import argparse
from collections import *
import numpy as np
import os
import csv
import json
#from target_words import *
#from make_csv import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Make json files for annotators.")
    parser.add_argument("--system", type=str,
                        help="System output file (clustering of lemma/form)")
    parser.add_argument("--corpus", type=str,
                        help="JSON document of the corpus")
    parser.add_argument("--output", type=str,
                        help="Output directory")
    args = parser.parse_args()

    corpus = json.load(open(args.corpus))
    
    lemmaPosForm = defaultdict(dict)
    with open(args.system) as fh:
        for line in fh:
            lemma, form, pos = line.strip().split()
            lemmaPosForm[lemma][pos] = form

    lexSplits = {}
    analogies = {}
            
    for lemma, pos2form in lemmaPosForm.items():
        for pos, form in pos2form.items():
            if form not in corpus:
                continue
            nExe = len(corpus[form])
            if form not in lexSplits:
                lexSplits[form] = [ { "name" : "%s_1" % form,
                                      "id" : 1,
                                      "word" : form,
                                      "examples" : "null",
                                      "selections" : [True for xx in range(nExe)] } ]
            if lemma not in lexSplits:
                lexSplits[lemma] = [ { "name" : "%s_1" % lemma,
                                       "id" : 1,
                                       "word" : form,
                                       "examples" : "null",
                                       "selections" : [True for xx in range(nExe)] } ]

            if pos not in analogies:
                idn = len(analogies)
                name = "%s_1~%s_1" % (lemma, form)
                provenance = "jin_etal"
                members = []
                analogy = { "id" : idn, "name" : name,
                            "provenance" : provenance,
                            "approved" : "false",
                            "selections" : [],
                            "members" : members }
                analogies[pos] = analogy
                
            analogies[pos]["members"].append( { "left" : [lemma, 1],
                                             "right" : [form, 1] } )
            analogies[pos]["selections"].append("false");

    analogies = list(analogies.values())
    final = { "lexicalInfo" : lexSplits, "analogies" : analogies }
    json.dump(final, open(args.output, "w"))
