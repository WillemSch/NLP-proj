import random
import re
from time import time
import pronouncing
import nltk
import pandas as pd
import similarity
from similarity import similarity_score
from similarity import to_tuple
from functools import lru_cache
from itertools import product as iterprod


arpabet = None
data_in_frames = []
link_re = re.compile(
    '(http[s]?://)?(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}([-a-zA-Z0-9()@:%_+.~#?&/=]*)'
)
hashtag_re = re.compile('#[-a-zA-Z0-9()@:%_+.~#?&/=…]*')
at_re = re.compile('@[-a-zA-Z0-9()@:%_+.~#?&/=…]*')


def load_data():
    path = "sarcasm_irony/train.csv"
    df = pd.read_csv(path)
    df.head()
    tweets = df.get("tweets")
    print("Pre-processing {0} tweets".format(len(tweets)))
    for index, tweet in enumerate(tweets):
        try:
            # Removes links from tweets
            tweet = re.sub(link_re, '', tweet)

            # TODO: only remove hsahtags at the end of a tweet? Others are words in the sentence
            tweet = re.sub(hashtag_re, '', tweet)

            # TODO: only remove @'s at the start of a tweet? Others are important for content
            tweet = re.sub(at_re, '', tweet)

            # Remove double spaces
            tweet = re.sub(' +', ' ', tweet)
        except Exception as e:
            # What goes wrong?
            pass

        if len(tweet.strip()) > 0:  # if no characters are left, discard the sentence
            try:
                frame = SentenceFrame(tweet.strip())
                # TODO: Split sentences if tweet has multiple
                data_in_frames.append(frame)
            except TypeError:
                # This tweet cannot be used because it contains no letters
                pass

    print("Finished pre-processing {0} tweets".format(len(tweets)))
    print("{0} usable tweets were found".format(len(data_in_frames)))


def find_rhyme(sentence):
    """
    Finds the rhyming part of a sentence (All phonemes from the last stressed syllable)
    :param sentence: A string containing the sentence
    :return: Returns the rhyming phonemes in a string, and the last actual word of the sentence in lowercase.
    """
    rhyme_tmp = re.sub(r'[^a-zA-Z ]*', '', sentence).strip()
    try:
        return pronouncing.rhyming_part(' '.join(get_phonemes(rhyme_tmp.split(' ')[-1])[0])), rhyme_tmp.split(' ')[-1].lower()
    except TypeError as _:
        print("Error with tweet: " + sentence)
        raise TypeError()


def word_syllable_count(word):
    '''
    returns syllable count of the word
    source: https://github.com/ypeels/nltk-book/blob/master/exercises/2.21-syllable-count.py
    '''

    vowels = {"AA", "AE", "AH", "AO", "AW", "AX", "AYR", "AY", "EH", "ER", "EY", "IH", "IX", "IY", "OW", "OY", "UH",
              "UW", "UX"}
    syllables = [to_tuple(ph) for ph in get_phonemes(word)[0]]
    return len([ph[0] for ph in syllables if ph[0] in vowels])


def calc_syllable_count(sentence):
    pronouncing.syllable_count(sentence)
    return 0


class SentenceFrame:
    rhyme = ''
    last_word = ''

    def __init__(self, sentence):
        # TODO: find subject per sentence, so we can generate a poem based on subject.
        self.sentence = sentence
        self.rhyme, self.last_word = find_rhyme(sentence)
        self.rhyme = self.rhyme.split(' ')
        # self.syllables = calc_syllable_count(sentence)

    def rhymes(self, other):
        own_rhyming_phonemes = (pronouncing.phones_for_word(self.rhyme)[0])
        other_rhyming_phonemes = pronouncing.rhyming_part(pronouncing.phones_for_word(other.rhyme)[0])
        # print(pronouncing.rhyming_part(pronouncing.phones_for_word(self.rhyme)))
        return other.rhyme in pronouncing.rhymes(self.rhyme)


@lru_cache()
def get_phonemes(s):
    """
    Returns a list of possible phonemes using the CMUDict. Also works for input strings that are not part of the
    CMUDict, by estimating phonemes of parts of the word.
    Source: https://stackoverflow.com/questions/33666557/get-phonemes-from-any-word-in-python-nltk-or-other-modules
    :param s: The word to get phonemes of.
    :return: A list of lists of possible phonemes.
    """

    global arpabet
    if arpabet is None:
        init_arpabet()
    s = s.lower()
    if s in arpabet:
        return arpabet[s]
    middle = len(s)/2
    partition = sorted(list(range(len(s))), key=lambda x: (x-middle)**2-x)
    for i in partition:
        # split the word into prefix & suffix if it is not in the CMUDict, and try again for the prefix and suffix.
        pre, suf = (s[:i], s[i:])
        if pre in arpabet and get_phonemes(suf) is not None:
            return [x+y for x,y in iterprod(arpabet[pre], get_phonemes(suf))]
    return None


def init_arpabet():
    global arpabet
    try:
        arpabet = nltk.corpus.cmudict.dict()
    except LookupError:
        # If the NLTK corpus is not loaded, dowload it
        nltk.download('cmudict')
        arpabet = nltk.corpus.cmudict.dict()


def score_rhyme(phones1, phones2):
    return similarity.score_rhyme(phones1, phones2)


def generate_poem(line_count, subject=None):
    poem = [None] * line_count  # Initialize an empty array of the size Line_count
    if subject:
        # TODO do something to select relevant sentences
        pass
    else:
        frame = data_in_frames[random.randint(0, len(data_in_frames))]
        # Find all sentences with similar rhyming phoneme length
        poem[0] = frame
        for i in range(1, line_count):
            if i % 4 < 2:  # if it is the 1st, 2nd, 5th, 6th... line pick new sentence (rhyming scheme: ababcdcd)
                poem[i] = data_in_frames[random.randint(0, len(data_in_frames))]
            else:
                poem[i] = rhyming_sentence(poem[i-2])
    return poem


def rhyming_sentence(prev_sentence):
    possible_rhymes = [x for x in data_in_frames if len(x.rhyme) == len(prev_sentence.rhyme) and x != prev_sentence]

    # Add all sentences who's rhyming score is greater than some value get added to an option list
    options = []
    options_different_word = []
    for other in possible_rhymes:
        score = score_rhyme(prev_sentence.rhyme, other.rhyme)
        if score > .6:
            if prev_sentence.last_word != other.last_word:
                options_different_word.append(other)
            else:
                options.append(other)

    # Pick a random option
    if len(options_different_word) > 0:
        # If there are options where the rhyming words are different prefer that one
        return options_different_word[random.randint(0, len(options_different_word)-1)]
    else:
        return options[random.randint(0, len(options)-1)]


if __name__ == '__main__':
    init_arpabet()
    load_data()

    print("Ready to generate poems")
    lines = input("How many lines should your poem have? (We are using rhyming scheme ababcdcd)")
    poem = generate_poem(8)
    for frame in poem:
        print(frame.sentence)
