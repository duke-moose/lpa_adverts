import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt')
import json

file = 'data/notice_dict_test_20200331.txt'

# Open dictionary of results
with open(file, 'r') as infile:
    test_dict = json.loads(infile.read())

def find_advertisements(parish, phrase_list):
    for article_number in test_dict[parish]:
        search_text = test_dict[parish][article_number]['text']
        text_sentences = sent_tokenize(search_text)
        if any(word in text_sentences[0] for word in phrase_list[parish]):
            count = 0
            for text in text_sentences:
                print(str(count), '::', text)
                count += 1
            print('\n')


key_words_dict_blank = {
    'East Baton Rouge': [' '],
    'Jefferson': [' '],
    'Ascension': [' '],
    'St. Tammany': [' '],
    'Bossier': [' '],
    'Washington': [' '],
}

key_words_dict = {
    'East Baton Rouge': [
        'INVITATION FOR PROFESSIONAL ENGINEERING SERVICES'
        'ADVERTISEMENT FOR BIDS',
        'NOTICE FOR ARCHITECTURAL SERVICES',
        'BID NOTICE',
        'ENGINEERING SERVICES WANTED'
    ],
    'Jefferson': [
        'NOTICE TO CONTRACTORS',
        'Notice of Request for Qualifications',
        'ADVERTISEMENT FOR BIDS',
    ],
    'Ascension': [
        'ADVERTISEMENT FOR BIDS',
        'Sealed bids',
    ],
    'St. Tammany': [
        'PUBLIC NOTICE ADVERTISEMENT FOR BIDS',
        'Click to view PDF'
    ],
    'Bossier': ['LEGAL NOTICE TO BIDDERS', 'ADVERTISEMENT FOR BIDS'],
    'Washington': ['Notice of Request for Qualifications', 'For Bids'],
}

'''Run this to search all dictionary results to help define key words
Step 1: Run this code.
Step 2: View key words in the 0:: line. Do they match the key words in the dictionary?
Step 3: Add new key words as necessary.'''
find_advertisements('East Baton Rouge', key_words_dict_blank)

'''Run this to search Parish for specific key words. After the key words are correct.'''
# find_advertisements('East Baton Rouge', key_words_dict)

# Todo figure out which sentences to keep from filter above.
#
