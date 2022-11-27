import pickle
import tgt
import glob
import sys


words_that_change_filepath = sys.argv[1]
path = sys.argv[2]
# Read data from file:
print("Will read from the `wordTranscriptions` pkl file.")
with open('wordTranscriptions.pkl', 'rb') as f:
    wordTranscriptions = pickle.load(f)


print("Will read the TextGrids and change the generated transcriptions from the intermediate form to the original form")

print("Useful debugging info for conversion is printed into the convertAlignments.message.log")
# The printing code was taken from https://stackoverflow.com/a/2513511
old_stdout = sys.stdout
log_file = open("convertAlignments.message.log", "w")
sys.stdout = log_file


if path[-1] !=  '/':
    path = path + '/'

def findClosestTranscription(transcriptionChanges,generated_intermediate_transcription):
    closest_transcription = transcriptionChanges[0]
    for transcriptionChange in transcriptionChanges[1:]:
        if transcriptionChange.intermediate_transcription == generated_intermediate_transcription:
            closest_transcription = transcriptionChange
    return closest_transcription

def replaceTranscription(transcriptionChange,generated_intermediate_transcription):
    predicted_intermediate_transcription = transcriptionChange.intermediate_transcription
    generated_intermediate_transcription_string = ' '.join(generated_intermediate_transcription)

    original_transcription = transcriptionChange.original_transcription
    original_transcription_string = ' '.join(original_transcription)
    segments_that_change = transcriptionChange.segments_that_change

    if generated_intermediate_transcription != predicted_intermediate_transcription:
        print(
            f"\tError! The TextGrid has an intermediate transcription '{generated_intermediate_transcription}' but that does not "
            f"\tmatch the intermediate transcription that our intermediate dictionary used '{predicted_intermediate_transcription}'")
        raise ValueError('There is an error, check the log file.')
        exit()

    print(f"\t\t\tThe word '{word}' has the intermediate transcription [{generated_intermediate_transcription_string}].\n"
          f"\t\t\tIt original transcription is [{original_transcription_string}].")
    if generated_intermediate_transcription == original_transcription:
        print(f"\t\t\t\tNo changes are needed because the two transcriptions are identical")
    elif len(original_transcription) == len(generated_intermediate_transcription):
        print(f"\t\t\tThe two transcriptions have the same length.")
        print(f"\t\t\tThe transcriptions differ in the following changes:")
        for segment_index in segments_that_change:
            segment_original = original_transcription[segment_index]
            segment_intermediate = generated_intermediate_transcription[segment_index]
            print(
                f"\t\t\t\tThe segment at index {segment_index} should change from [{segment_intermediate}] to [{segment_original}]")
            if generated_intermediate_transcription[segment_index] == segment_intermediate:
                print('\t\t\t\tOriginal:')
                print(f"\t\t\t\t\t{phone_intervals}")
                phone_intervals[segment_index].text = segment_original
                print('\t\t\t\tModified:')
                print(f"\t\t\t\t\t{phone_intervals}")
            else:
                print(f"\t\t\t\tError! The segment at index {segment_index} was not [{segment_intermediate}]")
                raise ValueError('There is an error, check the log file.')
                exit()


for textGridFilePath in glob.iglob(path + '**/*.TextGrid', recursive=True):
    tg = tgt.read_textgrid(textGridFilePath)
    print(f"\tProcessing the TextGrid {textGridFilePath}.")
# Verify that the TextGrid has only two tiers: words and phones
    if len(tg.tiers) !=  2:
        print(f"\tError! The TextGrid must have 2 tiers, but you have {len(tg.tiers)} tier(s).")
        raise ValueError('There is an error, check the log file.')
        exit()
    if tg.tiers[0].name != "words":
        print(f"\tError! The TextGrid's first tier must have the name 'words' but you have {tg.tiers[0].name}.")
        raise ValueError('There is an error, check the log file.')
        exit()
    wordTier = tg.get_tier_by_name("words")
    if tg.tiers[0].name != "words":
        print(f"\tError! The TextGrid's second tier must have the name 'phones' but you have {tg.tiers[1].name}.")
        raise ValueError('There is an error, check the log file.')
        exit()
    phoneTier = tg.get_tier_by_name("phones")


    # Will go through each word and convert its phone transcription back to the original IPA symbols
    for wordInterval in wordTier.annotations:
        print(f"\t\tProcessing the word: {wordInterval}")
        word = wordInterval.text
        if word not in wordTranscriptions:
        	print(f"\t\tErorr, the word {word} is missing from your pronunciation dictionary")
        	raise ValueError('There is an error, check the log file.')
        	exit()

        wordTranscription = wordTranscriptions[word]
        transcriptionChanges=wordTranscription.transcriptions
        phone_intervals = phoneTier.get_annotations_between_timepoints(wordInterval.start_time,
                                                                       wordInterval.end_time)
        generated_intermediate_transcription = [p.text for p in phone_intervals]
        print(f"\t\tThe TextGrid has the generated intermediate transcription: the word: {' '.join(generated_intermediate_transcription)}")

        if not wordTranscription.has_any_changes:
            print(f"\t\t\tThis word cannot have changes so we don't need to process it")
        else:
            print(f"\t\t\tThis word can have changes so we must process it")
            if len(transcriptionChanges)==1:
                print(f"\t\t\tThis word can has only one possible intermediate representation in the dictionary.")
                replaceTranscription(transcriptionChanges[0],generated_intermediate_transcription)
            else:
                print(f"\t\t\tThis word can has multiple possible intermediate representation in the dictionary.\n"
                      f"\t\t\tThey are")
                for transcriptionChange in transcriptionChanges:
                    print(transcriptionChange)
                print(f"\t\t\tWe must find the only identical one.")
                closest_transcription = findClosestTranscription(transcriptionChanges, generated_intermediate_transcription)
                print(f"\t\t\tThe closest transcription is:")
                print(closest_transcription)
                replaceTranscription(closest_transcription,generated_intermediate_transcription)
    print(f"\tThe new TextGrid is saved and replaced the original")
    tgt.write_to_file(tg,textGridFilePath,format='long')


sys.stdout = old_stdout
log_file.close()

print("The conversion is complete.")