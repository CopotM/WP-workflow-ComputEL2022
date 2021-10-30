if [ "$#" -ne 2 ]
then
  echo "Usage: bash run_newlemma_merge_uzh_baseline_prepare_seq2seq.sh test/dev <LANG>"
  exit 1
fi

source paths.sh

echo "USING $CODE_DIR $DATA_DIR $2 $TMP_DIR $OUTPUT_DIR"

python $CODE_DIR/pipeline/make_plausible_pairs.py --text $DATA_DIR/$2.txt --lemmas $DATA_DIR/$2.VERB-$1 --output $TMP_DIR/$2/plausible_pairs.txt
python $CODE_DIR/pipeline/compute_edittrees.py --pairs $TMP_DIR/$2/plausible_pairs.txt --output $TMP_DIR/$2/filtered_edittrees.pkl --verbose

# first time of new lemma discovery
python $CODE_DIR/pipeline/et_newlemma_once.py --text $DATA_DIR/$2.txt --lemmas $DATA_DIR/$2.VERB-$1 --et $TMP_DIR/$2/filtered_edittrees.pkl --new-lemma-weight 0.5 --output-et $TMP_DIR/$2/newlemma_edittrees.pkl --output-lemmas $TMP_DIR/$2/updated_lemmas_1.txt --verbose

python $CODE_DIR/pipeline/prep_unsupervised_pos.py --text $DATA_DIR/$2.txt --tmp-text $TMP_DIR/$2/lower_text.txt --tmp-ans $TMP_DIR/$2/pos_pseudo_answer.txt

# unsupervised pos tagging
$ANCHOR_EXT --output $TMP_DIR/$2/anchor --data $TMP_DIR/$2/lower_text.txt --train --unsup anchor --states 8 --triter 50
$ANCHOR_EXT --output $TMP_DIR/$2/anchor --data $TMP_DIR/$2/pos_pseudo_answer.txt --pred $TMP_DIR/$2/pos_pred.txt

python $CODE_DIR/pipeline/extract_tree_features.py --pos $TMP_DIR/$2/pos_pred.txt --et $TMP_DIR/$2/newlemma_edittrees.pkl --output $TMP_DIR/$2/tree_features.pkl --verbose
python $CODE_DIR/pipeline/merge_tree_by_features.py --et $TMP_DIR/$2/tree_features.pkl --output $TMP_DIR/$2/et_groups.pkl --verbose
python $CODE_DIR/pipeline/make_uzh_samples_byetgroups.py --et-groups $TMP_DIR/$2/et_groups.pkl --lemmas $DATA_DIR/$2.VERB-$1 --output-train $OUTPUT_DIR/PCS/$2/uzh.train --output-dev $OUTPUT_DIR/PCS/$2/uzh.dev --output-test $OUTPUT_DIR/PCS/$2/uzh.test --verbose
sort $OUTPUT_DIR/PCS/$2/*.{train,dev} > $OUTPUT_DIR/PCS/$2/uzh.all
python $CODE_DIR/pipeline/select_targets.py $OUTPUT_DIR/PCS/$2/uzh.all $DATA_DIR/$2.VERB-$1
