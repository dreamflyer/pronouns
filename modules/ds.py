import numpy as np

from wiki import data

from wiki import utils

from musket_core.datasets import PredictionItem

import pymagnitude

m_path = "/Users/dreamflyer/Downloads/glove-lemmatized.6B.300d.magnitude"

vectors = pymagnitude.Magnitude(m_path)

none = vectors.query("none")

def convert_name(name):
    tokens = utils.stoa_1(name)

    result = []

    size = len(tokens)

    for i in range(size):
        result.append(' '.join(tokens[0: i + 1]))

    result.reverse()

    return result

def sample_text(record, isBroken):
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

    return text

class DS:
    def __init__(self):
        self.reader = data.DataReader("/Users/dreamflyer/Downloads/gap-coreference-master/gap-development.tsv", "/Users/dreamflyer/PycharmProjects/untitled/wiki/wiki")

        self.ids = self.reader.get_ids()

    def __getitem__(self, item):
        id = self.ids[item]

        it = self.reader.item(id)

        broken = np.random.choice([0.0, 1.0])

        sample = sample_text(it, broken)

        tokens = utils.stoa(sample)

        vs = vectors.query(tokens)

        vslen = len(vs)

        if vslen > 100:
            vs = vs[: 100]
        else:
            nones = np.zeros((100 - vslen, 300))

            nones[:] = none

            vs = np.concatenate((vs, nones), 0)

        return PredictionItem(id, vs, np.array([broken]))

    def __len__(self):
        return len(self.ids)


def getTrain():
    return DS()
