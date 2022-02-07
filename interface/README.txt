How to use the demo interface:

* cd into the interface directory
* run an http server: python -m http.server
* navigate to localhost:8000
* you should see a directory with a list of files; click quasar-analogy.html
* the corpus and examples for the ComputeEL English dataset is preloaded
  - currently, loading another corpus requires a code change
* you can load and save sets of analogy annotations
  - to view the Jin et al. clustering of these English verbs, use:
    File -> Load state -> (select en-uzh.json) -> Upload
* The top left panel shows the current analogies
* If you click an analogy, its members are displayed at lower left
* Type a word in the lexicon browser at upper right (or select from
  the "Show list" dropdown) to view the current lexical splits
  (unique concordances) associated with it
  - click one of these lexical splits to view its paradigm and the
    "Edit concordance" dropdown
  - hit "Edit concordance" to view and change the list of tokens in context
* If you make edits and want to save them, use File -> Save state
  - at the moment, you do not get to choose the filename

To create a new dataset file, use:

python dump_corpus.py --corpus <UD corpus> --system <uzh.final file for that language> --output <output.json>

To create a new system state from Jin et al. output, use:

python dump_analogies.py --system <uzh.final> --corpus <json file from previous step> --output <output.json>
