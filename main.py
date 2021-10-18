import pronouncing
import nltk
from similarity import similarity_score
from functools import lru_cache
from itertools import product as iterprod


arpabet = None


def find_rhyme(sentence):
    return sentence.split(' ')[-1]


def calc_syllable_count(sentence):
    return 0


class SentenceFrame:
    rhyme = ''

    def __init__(self, sentence):
        self.sentence = sentence
        self.rhyme = find_rhyme(sentence)
        self.syllables = calc_syllable_count(sentence)

    def rhymes(self, other):
        own_rhyming_phonemes = pronouncing.rhyming_part(pronouncing.phones_for_word(self.rhyme)[0])
        other_rhyming_phonemes = pronouncing.rhyming_part(pronouncing.phones_for_word(other.rhyme)[0])
        # print(pronouncing.rhyming_part(pronouncing.phones_for_word(self.rhyme)))
        return other.rhyme in pronouncing.rhymes(self.rhyme)


@lru_cache()
def get_phonemes(s):
    '''
    Returns a list of possible phonemes using the CMUDict. Also works for input strings that are not part of the
    CMUDict, by estimating phonemes of parts of the word.
    Source: https://stackoverflow.com/questions/33666557/get-phonemes-from-any-word-in-python-nltk-or-other-modules
    :param s: The word to get phonemes of.
    :return: A list of lists of possible phonemes.
    '''
    global arpabet
    if arpabet is None:
        init_arpabet()
    s = s.lower()
    if s in arpabet:
        return arpabet[s]
    middle = len(s)/2
    partition = sorted(list(range(len(s))), key=lambda x: (x-middle)**2-x)
    for i in partition:
        pre, suf = (s[:i], s[i:])
        if pre in arpabet and get_phonemes(suf) is not None:
            return [x+y for x,y in iterprod(arpabet[pre], get_phonemes(suf))]
    return None


def init_arpabet():
    global arpabet
    try:
        arpabet = nltk.corpus.cmudict.dict()
    except LookupError:
        nltk.download('cmudict')
        arpabet = nltk.corpus.cmudict.dict()


def score_rhyme(phones1, phones2):
    #TODO: Score rhymes based on their phonemes and stress.
    pass


if __name__ == '__main__':
    init_arpabet()
    print(similarity_score('AA1', 'T'))
    print(similarity_score('AE1', 'AE1'))
    print(similarity_score('AA1', 'AE1'))
    print(similarity_score('AA0', 'AE1'))
