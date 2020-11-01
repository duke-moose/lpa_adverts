import nltk
from nltk.tokenize import sent_tokenize
import json
from nltk.corpus import stopwords
import pprint
from collections import OrderedDict

# Dictionary of all keywords to search advertisements for each Parish
key_words_advertisement_dict = {
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

class LpaAdvertisementReader:
    def __init__(self, advert_dict, parish):
        self.advert_dict = advert_dict  # advert_dict: Parish[advert_number]['paper', 'date', 'text']
        self.parish = parish

    def one_advertisement(self, parish, advert_number):
        search_text = self.advert_dict[parish][str(advert_number)]
        return search_text

    def filter_advertisements_key_word(self, parish, key_word_dict=None):
        filtered_advertisements_dict = OrderedDict()
        if key_word_dict is None:
            key_word_dict = {str(parish): ' '}
        for article_number in self.advert_dict[parish]:
            search_text = self.advert_dict[parish][article_number]['text']
            if any(word in search_text for word in key_word_dict[parish]):
                filtered_advertisements_dict[article_number] = self.advert_dict[parish][article_number]
        return filtered_advertisements_dict

    def token_and_tag_words(self, advertisement):
        toke_sentences = nltk.sent_tokenize(advertisement['text'])
        stop_words = set(stopwords.words("english"))
        count = 0
        all_toke_words = []
        short_toke_words = []
        pos_tags = []
        for sentence in toke_sentences:
            words_tokenize = nltk.word_tokenize(sentence)
            words = [w for w in words_tokenize if w not in stop_words]
            tagged_words = nltk.pos_tag(words)

            all_toke_words.append(words_tokenize)
            short_toke_words.append(words)
            pos_tags.append(tagged_words)

            # count += 1
            # if count > 2:
            #     break
        return toke_sentences, all_toke_words, short_toke_words, pos_tags

    def regex_filter_words(self, tagged_sentences):
        keep = []
        for tagged_words in tagged_sentences:
            grammar_regex = """
                            P: {<:><NNP>+<CC><NNP>+}
                            P: {<:><NNP>*}
                            P: {<DT><NN><VBZ><.*>+}
                            """
            rp = nltk.RegexpParser(grammar_regex)
            parsed_sentence = rp.parse(tagged_words)
            # print('results: ', len(parsed_sentence))
            keep_sentences = [keep for keep in parsed_sentence if len(keep) > 2]
            if keep_sentences:
                # print(keep_sentences)
                keep.append(keep_sentences)
        return keep

    def run(self):
        # 1. Filter advertisements for key words, see dictionary above
        filter_adverts = self.filter_advertisements_key_word(
            parish=self.parish,
            key_word_dict=key_words_advertisement_dict
        )
        # pprint.pprint(filtered_advertisements)
        for advert_number in filter_adverts: # Focus on one advertisement at a time.
            print(advert_number)
            # 2. Tokenize sentences, words, and remove stop words.
            # token_s = nltk.sent_tokenize(filter_adverts[advert]['text'])
            sentences, all_words, short_words, tags = self.token_and_tag_words(filter_adverts[advert_number])
            # print(all_words)
            # print(short_words)
            # print(tags)
            print(self.regex_filter_words(tags))


        # Todo figure out which sentences to keep from filter above.
        #

if __name__ == "__main__":
    '''Run this to search all dictionary results to help define key words
    Step 1: Run this code.
    Step 2: View key words in the 0:: line. Do they match the key words in the dictionary?
    Step 3: Add new key words as necessary.'''

    file = '../data/notice_dict_test_20200331.txt'
    # Open dictionary of results
    with open(file, 'r') as infile:
        test_dict = json.loads(infile.read())
    # LpaAdvertisementReader(test_dict, 'East Baton Rouge').run()
    LpaAdvertisementReader(test_dict, 'Jefferson').run()

    ''' Run Single Advertisement '''
    # pprint.pprint(LpaAdvertisementReader(test_dict).one_advertisement('East Baton Rouge', 6))
    # lpa = LpaAdvertisementReader(test_dict)
    # single = lpa.one_advertisement('East Baton Rouge', 6)
    # sentences, all_words, short_words, tags = lpa.token_and_tag_words(single)
    # keep_phrases = lpa.regex_filter_words(tags)
    # c = 0
    # for k in keep_phrases:
    #     print(k)
    # for s in sentences:
    #     # print(c)
    #     # print(s)
    #     if c in [18, 35, 53, 69, 87, 101, 116]:
    #         print(c)
    #         print(s)
    #         try:
    #             print(tags[c])
    #         except:
    #             pass
    #     c += 1





    # text = "learn php from guru99"
    # tokens = nltk.word_tokenize(text)
    # print(tokens)
    # tag = nltk.pos_tag(tokens)
    # print(tag)
    # grammar = "NP: {<DT>?<JJ>*<NN>}"
    # cp = nltk.RegexpParser(grammar)
    # result = cp.parse(tag)
    # print(result)
    # result.draw()    # It will draw the pattern graphically which can be seen in Noun Phrase chunking