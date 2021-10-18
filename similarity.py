import re


def similarity_score(phoneme1, phoneme2):
    ptuple1 = to_tuple(phoneme1)
    ptuple2 = to_tuple(phoneme2)
    print(ptuple1)
    print(ptuple2)

    if phoneme1 == phoneme2:
        return 1
    #TODO: Add similarity scores example:
    if ptuple1[0] == "AA":
        if ptuple2[0] == "AE":
            score = .8
        elif ptuple2[0] == "AH":
            score = .5
        elif ptuple2[0] == "AX":
            score = .7
        elif ptuple2[0] == "EH":
            score = .7
        else:
            score = 0
    else:
        score = 0

    # If the phoneme has stress on it adjust score to difference in stress
    if ptuple1[1] is not None and ptuple2[1] is not None:
        difference = abs(int(ptuple1[1]) - int(ptuple2[1]))
        score *= .8 + (.1 * (2 - difference))

    return score


def to_tuple(phoneme):
    match = re.match(re.compile('([A-Z]+)([0-2])?'), phoneme)
    letters = match.group(1)
    addition = match.group(2)
    return [letters, addition]
