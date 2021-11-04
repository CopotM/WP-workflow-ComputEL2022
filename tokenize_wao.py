import sys
import os
import glob
from nltk.tokenize import wordpunct_tokenize

if __name__ == "__main__":
    dd = sys.argv[1]
    out = sys.argv[2]

    if dd.endswith(".txt"):
        path = dd
    else:
        path = dd + "/*.txt"

    with open(out, "w") as ofh:

        for fname in glob.glob(path):
            print(fname)
            with open(fname) as fh:
                for line in fh:
                    tokens = wordpunct_tokenize(line)
                    ofh.write(" ".join(tokens) + "\n")

