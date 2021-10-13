import pronouncing


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


if __name__ == '__main__':
    sentence1 = SentenceFrame("Rhyming is in my god")
    sentence2 = SentenceFrame("Call me a rhyming university")
    print(sentence2.rhymes(sentence1))
