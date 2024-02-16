import codecs
import pickle
import sys

from WordTranscriptionAndChanges import *

pronDict_original_filepath = sys.argv[1]
phone_mapping_filepath = sys.argv[2]
pronDict_intermediate_filepath = sys.argv[3]

	
# Read the phone_mapping file and create a dict object out of it
phone_mapping = {}
# The phone_mapping dictionary has a simple structure of: phone_mapping[original_segment]=intermediate_segment
with codecs.open(phone_mapping_filepath, 'r', 'utf-8') as phone_mapping_file:
    print("Will read the phone mapping file.")
    phone_lines = phone_mapping_file.read().splitlines()
    phone_lines[0] = phone_lines[0].replace('\ufeff', "")
    for phone_line in phone_lines:
        phone_line = phone_line.split('\t')

        if len(phone_line) != 2:
            print(f"Error, the line `{phone_line}` in the phone mapping file is NOT tab-separated with two columns."
                  f"\nMake sure all your lines are tab-separated with two columns.")
            raise ValueError('There is an error, check the log file.')
            exit()

        original_phone, intermediate_phone = phone_line
        if original_phone in phone_mapping:
            print(f"Error, the phone {original_phone} appears multiple times in the phone mapping file."
                  f"\nMake sure all the phones from the original language are unique.")
            raise ValueError('There is an error, check the log file.')
            exit()
        phone_mapping[original_phone] = intermediate_phone


# Read the original pronunciation dictionary that had the original transcriptions.
# Create a new dictionary with intermediate transcriptions by applying the custom phone mapping
# Store information on the transcriptions that changed into a dict called `wordTranscriptions`
wordTranscriptions = {}

# The transcription_conversions dict  is made up of words whose transcriptions did or did not change.
# Each word maps to a wordTranscription object.
# A wordTranscription object contains the word's original transcription, intermediate transcriptions, and the list of segment changes
# e.g. = transcription_conversions =  { "ըսաւ": obj0,   "ասաց": obj1,  "բառ": obj2,  "րա": obj3 ,  "ռա": obj3 }
# }
# The word ըսաւ has an unchanged transcription form ["ə","s","ɑ","v"]
# The word ասաց has a single alteration from ["ɑ","s","ɑ","t͡sʰ"] to ["ɑ","s","ɑ","tʃ"] at index 3
# The word բառ has a single intermediate forms with two alternations, from  ["p", "ʏ", "r"] to ["p", "u", "ɾ"] at indexes 1,2
# The word րա has two intermediate forms, with zero or one alteration,
#   from ["ɾ","ɑ"] to ["ɾ","ɑ"] with zero changes, or  ["ɻ","ɑ"] to ["j","ɑ"] with change at index 0
# The word ռա has two identical intermediate forms from ["ɾ","ɑ"] or ["r","ɑ"] to ["ɾ","ɑ"] at index 0


def convert_transcription_to_intermediate(original_transcription):
    # Convert an original transcription into the intermediate transcription (even if identical) by using the custom phone_mapping dict.
    # Keep track of the changes if any

    # transcriptionChange:  original_transcription, intermediate_transcription, segments_that_change, didChange):
    intermediate_transcription = []
    segments_that_change = []
    for i in range(len(original_transcription)):
        original_segment = original_transcription[i]
        if original_segment in phone_mapping:
            intermediate_segment=phone_mapping[original_segment]
            intermediate_transcription.append(intermediate_segment)
            segments_that_change.append(i)
        else:
            intermediate_transcription.append(original_segment)
    transcriptionChange = TranscriptionChange(original_transcription,intermediate_transcription,segments_that_change)
    return transcriptionChange

print("Will read the original pronunciation dictionary and create an intermediate pronunciation dictionary")
# Read the original pronunciation dictionary and create a modified dictionary with English IPA symbols

print("Useful debugging info for conversion is printed into the convertPronDict.message.log")
# The printing code was taken from https://stackoverflow.com/a/2513511
old_stdout = sys.stdout
log_file = codecs.open("convertPronDict.message.log", "w", 'utf-8')
sys.stdout = log_file


with codecs.open(pronDict_original_filepath, 'r', 'utf-8') as pronDict_original_file:
    with codecs.open(pronDict_intermediate_filepath, 'w', 'utf-8') as pronDict_intermediate_file:
        dictionary_lines = pronDict_original_file.read().splitlines()
        dictionary_lines[0] = dictionary_lines[0].replace('\ufeff', "")
        for dictionary_line in dictionary_lines:
            print(f"\tProcessing the following line from the original pronunciation dictionary: {dictionary_line}")
            dictionary_line = dictionary_line.split('\t')
            if len(phone_line) != 2:
                print(f"\tError, the line `{dictionary_line}` in the original pronunciation dictionary file is NOT tab-separated with two columns."
                      f"\nMake sure all your lines are tab-separated with two columns.")
                raise ValueError('There is an error, check the log file.')
                exit()

            word,original_transcription_string = dictionary_line[0].strip(),  dictionary_line[1].strip()
            original_transcription = original_transcription_string.split(' ')
            transcriptionChange=convert_transcription_to_intermediate(original_transcription)
            intermediate_transcription_string = ' '.join(transcriptionChange.intermediate_transcription)
            if word not in wordTranscriptions:
                print(f"\t\tThe word {word} is newly encountered")
                newWordTranscription = WordTranscription(word)
                print(f"\t\tIts original transcription {original_transcription_string} is converted to {intermediate_transcription_string}.")
                newWordTranscription.add_transcription(transcriptionChange)
                wordTranscriptions[word] = newWordTranscription
            else:
                print(f"\t\tThe word {word} is previously encountered")
                print(f"\t\tIts original transcription {original_transcription_string} is converted to {intermediate_transcription_string}.")
                wordTranscriptions[word].add_transcription(transcriptionChange)

            pronDict_intermediate_file.write(f"{word}\t{intermediate_transcription_string}\n")

print(f"The word transcriptions are as follows:")
for wordTranscription in wordTranscriptions.items():
    print(str(wordTranscription[1]))

sys.stdout = old_stdout
log_file.close()

print("The pickle object `wordTranscriptions.pkl` is created. It is a Python dictionary that keeps track of the changes.")
with open('wordTranscriptions.pkl', 'wb') as f:
    pickle.dump(wordTranscriptions, f)


