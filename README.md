# Interlingual MFA

This repository contains Python scripts and workflow for a) taking an [MFA](montreal-forced-aligner.readthedocs.io/) forced alignment model that was trained for one language, and b) running that model onto a different language. 

I tested the code with some [Armenian data](https://github.com/jhdeov/armenian-intonation/tree/main) by aligning with an English model (and some other high-resource models). The alignment seems to work well.

The code has also been tested on Kalmyk speech from the [INEL Corpus](https://inel.corpora.uni-hamburg.de/portal/corpora/kalmyk/#en) with both English and French models. The English models produced the best alignments.

# Background
The rationale is that for low-resource languages, it takes a lot of data (sound files, transcriptions, pronunciation dictionaries) to create a high-quality alignment model. As a stepping stone, you can run a model from a high-resource language (like English) onto your low-resource language (like Armenian). The generated alignments seem to be quite sensible. In my anecdotal experience, the alignments I get from an English-based model (that's trained on over >1000hrs) are better than the alignments from a custom-made model (based on 1-20hrs of data). 

# Workflow

The following workflow explains the steps to running the scripts alongside MFA. There are example files in [Examples](/Examples/). A lot of the background work was done thanks to [textgrid](https://github.com/kylebgorman/textgrid). 


## Before you begin

1. Ensure that MFA is running on your system. 
2. Ensure you have a high-resource acoustic model like the `english_mfa`. 
3. Ensure you have an original pronunciation dictionary, called `pronDictOriginal.txt`. 
The dictionary should have the format of `word IPA`

## Procedure
1. Review the [list of phones] in the `english_mfa` model.

2. Create a phone mapping file like `phoneMapping.txt`. 

This file will map phones that exist in the low-resource language's pronunciation dictionary `pronDictOriginal.txt` but which are absent in `english_mfa`.

For every such non-English phone, write an approximate English phone. For example, a non-English trill /r/ can be approximated and mapped to an English flap /ɾ/. For example, see [here](/Examples/phoneMapping.txt).

3. Convert your original dictionary `pronDictOriginal.txt` into an intermediate dictionary `pronDictIntermediate.txt` by running the following command:

`python convertPronDict.py  pronDictOriginal.txt phoneMapping.txt pronDictIntermediate.txt`

This command will replace the non-English phones with English phones. The script should return errors if there any issues in your original dictionary or phone-mapping file. 

4. Keep note of the generated file `wordTranscriptions.pkl` which will be used to transfer information about the dictionary across the Python files.

5. Validate MFA on your dictionary and corpus to make sure there are no non-English phones. 

`mfa validate $CORPUS_DIRECTORY pronDictIntermediate.txt english_mfa  --ignore_acoustics`

6. Run the MFA aligner on your corpus with the intermediate dictionary. 

`mfa align $CORPUS_DIRECTORY pronDictIntermediate.txt english_mfa $OUTPUT_DIRECTORY --clean --overwrite`

7. Convert the generated alignments from English phones back to non-English phones.

`python convertAlignments.py wordTranscriptions.pkl $OUTPUT_DIRECTORY`


# Open issues and future work

There are measures to minimize variation in the data. But I haven't yet incorporated fixes for some likely common errors.

* You can have words that have multiple possible pronunciations. However, the conversion codes currently cannot support converting an alignment where a segment was deleted. To allow this level of flexibility, the conversion would likely need to incorporate a type of `shortest edit distance` algorithm.
* I haven't tested out the conversion scripts with funny edge cases like case-sensitivity. 

It would be interesting to also use this workflow to examine how different high-resource language models handle the same data from different languages. Feel free to contact me if you have any ideas for collaboration or fixes.
