# ACL 2021 project (let's find this bad boy a title!)

Project GoogleDoc: https://docs.google.com/document/d/1knRWK6CBbDS5rMTyEZtRPXYs5g4EPp4KMtwjcNplp-E/edit \n
Overleaf writeup: https://www.overleaf.com/3759535975swrtvqbyptmw \n
Annotation guidelines: shorturl.at/gAC27 \n

First, clone the repository locally. 

Once you've annotated the file for a lexeme, you should run the file *regex_lexeme.py* in order to find any other occurrences of the lexeme that have not been picked up by the baseline. 

The programme has 5 arguments:
- --repository: the local file path for the ACL_2021 git repository
- --language: are you annotating English or Croatian? (case doesn't matter)
- --lexeme: the name of the lexeme you've just finished annotating. This is the file name without the .txt extension. 
- --regex: the regex you want to generate an annotation file from. The word form should be within a capturing group.
  -  For example, if you've annotated the lexeme *apply* and you only found the forms "apply" and "applying", you might want to look for instances of "applied" or even "application". The regex **"(appli.+?)\\\b"** will pick up those occurrences. Forms that were already identified by the method as belonging to the lexeme of interest will not feature, even if they match the regex.
    -  It's important that you place it between quotation marks, and that you escape the backslash.
  - The annotation file thus obtained will be in *ACL_2021/annotate/regex_output/{lexeme}.csv*
  - If no matches were found for your regex, the file will still be created. Its content is a string explaining that no matches were found.
  - If an annotation file for that lexeme already exists in the directory, the programme will add a number to the filename. This helps avoid accidentally overwriting your work.
- --n_lemma: how many occurrences do you want the programme to output? Default is 20.


