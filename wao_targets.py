import sys
from collections import *

if __name__ == "__main__":
    corpus = sys.argv[1]

    counts = Counter()

    with open(corpus) as fh:
        for line in fh:
            words = line.strip().split()
            counts.update([xx.lower() for xx in words if xx.isalpha()])

    for ind, (word, ct) in enumerate(counts.most_common(150)):
        if ind > 10:
            print(word)
