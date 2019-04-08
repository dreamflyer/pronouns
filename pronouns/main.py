import numpy as np

from wiki import data

from wiki import utils

import tqdm

reader = data.DataReader("/Users/dreamflyer/Downloads/gap-coreference-master/gap-development.tsv", "wiki")

trues1 = 0

falses1 = 0

nones = 0

def gtrue(record):
    isa = record['A-coref'] == 'TRUE'
    isb = record['B-coref'] == 'TRUE'

    is_none = not (isa or isb)

    return np.array([0 + isa, 0 + isb, 0 + is_none])

def convert(val):
    return max(min(val, 1 - 1e-15),1e-15)


def is_eq(v1, v2):
    return v1[0] == v2[0] and v1[1] == v2[1] and v1[2] == v2[2]

def suggest_by_headers(record):
    wiki = "" + record['wiki_content'].lower()

    isa = record['A-coref'] == 'TRUE'
    isb = record['B-coref'] == 'TRUE'

    A = "" + record['A'].lower()
    B = "" + record['B'].lower()

    H = "" + record['title'].lower()

    h_tokens = utils.stoa_1(H)

    a_tokens = utils.stoa_1(A)
    b_tokens = utils.stoa_1(B)

    a = wiki.count(a_tokens[0])
    b = wiki.count(b_tokens[0])

    res = 3.1

    result = [1, 1, 1]

    if a_tokens[0] in h_tokens:
        result[0] = res

    if b_tokens[0] in h_tokens:
        result[1] = res

    # if a > b:
    #     result = [res, 1, 1]
    # else:
    #     result = [1, res, 1]

    result = np.array(result)

    summ = sum(result)

    if summ > 0:
        result = result / summ

    result = [convert(item) for item in result]

    return np.array(result)

def convert_name(name):
    tokens = utils.stoa_1(name)

    result = []

    size = len(tokens)

    for i in range(size):
        result.append(' '.join(tokens[0: i + 1]))

    result.reverse()

    return result

#Alex Charlie

def sample(record, isBroken):
    A = "" + record['A'].lower()
    B = "" + record['B'].lower()

    P = "" + record['Pronoun'].lower()

    off = int(record['Pronoun-offset'])


    text = "" + record['Text'].lower()

    a_names = convert_name(A)
    b_names = convert_name(B)

    t1 = text[: off]

    t2 = text[off: ]

    #t2 = t2.replace(P, "P#" + P.upper(), 1)

    if isBroken:
        isa = record['A-coref'] == 'TRUE'
        isb = record['B-coref'] == 'TRUE'

        if isa:
            t2 = t2.replace(P, "B#NAME", 1)
        elif isb:
            t2 = t2.replace(P, "A#NAME", 1)
        else:
            rnd = np.random.choice([0, 1])

            if rnd:
                t2 = t2.replace(P, "B#NAME", 1)
            else:
                t2 = t2.replace(P, "A#NAME", 1)

    text = t1 + t2

    for item in a_names:
        text = text.replace(item, "A#NAME")

    for item in b_names:
        text = text.replace(item, "B#NAME")

    text = text.replace("A#NAME", "alex").replace("B#NAME", "charlie")

    print(len(utils.stoa(text)))

    return text

def tst(record):
    A = "" + record['A'].lower()
    B = "" + record['B'].lower()

    P = "" + record['Pronoun'].lower()

    off = int(record['Pronoun-offset'])


    text = "" + record['Text'].lower()

    a_names = convert_name(A)
    b_names = convert_name(B)

    t1 = text[: off]

    t2 = text[off: ]

    t2 = t2.replace(P, "P#" + P.upper(), 1)

    text = t1 + t2

    for item in a_names:
        text = text.replace(item, "Alex")

    for item in b_names:
        text = text.replace(item, "Charlie")

    print("############")

    print(A)
    print(B)

    print("original: + " + record['Text'])

    #print("replaced: + " + text)

def suggest_by_count(record):
    wiki = "" + record['wiki_content'].lower()

    isa = record['A-coref'] == 'TRUE'
    isb = record['B-coref'] == 'TRUE'

    A = "" + record['A'].lower()
    B = "" + record['B'].lower()

    a_tokens = utils.stoa_1(A)
    b_tokens = utils.stoa_1(B)

    a = wiki.count(a_tokens[0])
    b = wiki.count(b_tokens[0])

    res = 3.1

    if a > b:
        result = [res, 1, 1]
    else:
        result = [1, res, 1]

    result = np.array(result)

    summ = sum(result)

    if summ > 0:
        result = result / summ

    result = [convert(item) for item in result]

    return np.array(result)

def suggest_random(record):
    pred = gtrue(record)

    pred = np.random.rand(3)

    #pred[2] = 0

    #pred = [1, 1, 1]

    pred = pred / np.sum(pred)

    result = [convert(item) for item in pred]

    return np.array(result)

def log_metric(suggestions, gtrue):

    return -np.sum(gtrue * np.log(suggestions)) / suggestions.shape[0]

ids = reader.get_ids()

#ids = [item for item in ids if reader.item(item)['A-coref'] == 'TRUE' or reader.item(item)['B-coref'] == 'TRUE']

size = len(ids)

trues = np.zeros((size, 3))
suggestions_r = np.zeros((size, 3))
suggestions_b = np.zeros((size, 3))
suggestions_h = np.zeros((size, 3))

count = 0

for item in tqdm.tqdm(ids, leave=True):
    record = reader.item(item, True)

    trues[count] = gtrue(record)
    suggestions_r[count] = suggest_random(record)
    suggestions_b[count] = suggest_by_count(record)
    suggestions_h[count] = suggest_by_headers(record)

    a = sample(record, True)

    # print("---------")
    #
    # print(a)

    #tst(record)

    count += 1

res = log_metric(suggestions_r, trues)

print("random: " + str(res))

res = log_metric(suggestions_b, trues)

print("euristic_count: " + str(res))

res = log_metric(suggestions_h, trues)

print("euristic_header: " + str(res))


