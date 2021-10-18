import re


def similarity_score(phoneme1, phoneme2):
    '''

    :param phoneme1:
    :param phoneme2:
    :return:
    '''

    ptuple1 = to_tuple(phoneme1)
    ptuple2 = to_tuple(phoneme2)
    print(ptuple1)
    print(ptuple2)

    if phoneme1 == phoneme2:
        return 1

    phones = sorted([ptuple1[0], ptuple2[0]])
    score = similarity_dict[phones[0], phones[1]]
    if score is None:
        score = 0

    # If the phoneme has stress on it adjust score to difference in stress
    if ptuple1[1] is not None and ptuple2[1] is not None:
        difference = abs(int(ptuple1[1]) - int(ptuple2[1]))
        score *= .8 + (.1 * (2 - difference))

    return score


def to_tuple(phoneme):
    '''
    Split phonemes into their phonetic description and possible
    :param phoneme:
    :return:
    '''
    match = re.match(re.compile('([A-Z]+)([0-2])?'), phoneme)
    letters = match.group(1)
    addition = match.group(2)
    return [letters, addition]


similarity_dict = {
    "AA": {
        "AE": .9,
        "AH": .9,
    },
    "AE": {

    },
    # TODO...
}
