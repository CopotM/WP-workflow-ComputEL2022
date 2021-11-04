# The commands used to create these files.

cat ../wao/NT/* >> nt.txt
sed -e s/æ̈/ë/g -e s/æ/e/g nt.txt > nt-ashless.txt
grep -Eo '\w+|[^\w ]' nt-ashless.txt >nt-ashless-tokenized.txt
(grep -Eo "[^[:space:]]{3,}[mb]ipa" nt-ashless-tokenized.txt |sed s/[mb]ipa//g ;
grep -Eo "[^[:space:]]{3,}[dn]änipa" nt-ashless-tokenized.txt |sed s/[dn]änipa//g ;
grep -Eo "[^[:space:]]{3,}ngampa" nt-ashless-tokenized.txt| sed s/ngampa//g) | sed -e s/ë$/e/ -e s/ï$/i/ -e s/ä$/a/ -e s/ö$/o/ | sort|uniq  > lexeme.txt
