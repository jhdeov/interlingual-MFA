
class TranscriptionChange:
    # Information about a single mapping from an original transcription to an intermediate transcription
    # We keep track of:
    #   - the intermediate transcription
    #   - the index of the segments that changed
    #   - whether this intermediate transcription is different from the original transcription
    def __init__(self, original_transcription, intermediate_transcription, segments_that_change):
        self.original_transcription = original_transcription
        self.intermediate_transcription = intermediate_transcription
        self.segments_that_change = segments_that_change
        if original_transcription == intermediate_transcription:
            self.didChange = False
        else: self.didChange = True
    def __str__(self):
        stringObject = f"Original transcription: {self.original_transcription}\n" \
                       f"Intermediate transcription: {self.intermediate_transcription}\n" \
                       f"Segments that change: {self.segments_that_change}\n" \
                       f"Did it change: {self.didChange}"
        return stringObject
class WordTranscription:
    # Information about a word and its transcriptions
    # We keep track of the word and a list of its transcriptions (in the form of transcriptionChange objects)
    def __init__(self,word):
        self.word = word
        self.transcriptions=[]
        self.has_any_changes = False
    def add_transcription(self,transcriptionChange):
        self.has_identical_intermediate_transcriptions(transcriptionChange)
        self.transcriptions.append(transcriptionChange)
        if transcriptionChange.didChange:
            self.has_any_changes = True
    def __str__(self):
        stringObject = f"Word: {self.word}\n" \
                       f"Does it have any changes: {self.has_any_changes}\n" \
                       f"Transcriptions:\n"
        for transcription in self.transcriptions:
            stringObject = stringObject + str(transcription) + "\n"
        return stringObject

    def has_identical_intermediate_transcriptions(self,current_transcriptionChange):
        for previous_transcriptionChange in self.transcriptions:
            if previous_transcriptionChange.intermediate_transcription == current_transcriptionChange.intermediate_transcription:
                previous_intermediate_transcription = ' '.join(previous_transcriptionChange.intermediate_transcription)
                current_intermediate_transcription = ' '.join(current_transcriptionChange.intermediate_transcription)
                previous_original_transcription = ' '.join(previous_transcriptionChange.original_transcription)
                current_original_transcription = ' '.join(current_transcriptionChange.original_transcription)
                if current_intermediate_transcription ==previous_intermediate_transcription:
                    print(f"Error! The intermediate transcription [{current_intermediate_transcription}] is generated multiple times for"
                          f" the word {self.word} because your custom phone mapping creates an ambiguity.\n"
                          f"The intermediate form is generated from both original [{current_original_transcription}] and [{previous_original_transcription}].")
                    print(f"You must do one of the following changes:\n"
                          f"1) In the original dictionary, delete one of the original transcriptions.\n"
                          f"2) In the original dictionary, combine the two original transcriptions.\n"
                          f"For combination, if the two original transcritpions are ['a' 'b'] and ['æ' 'b'] where 'a' and 'æ' are mapped to 'a',"
                          f" use instead ['a/æ' 'b'].\n"
                          f"Then in the phone mapping file, add the line `a/æ a`.\n"
                          f"You then have to manually go to the final alignment files, and manually change `a/æ` to either `a` or `æ`. ")
                raise ValueError('There is an error, check the log file.')
                exit()
