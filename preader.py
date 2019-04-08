import wikipedia

import requests

import csv

import os

import pickle

import tqdm

import urllib

import nltk

import re

import matplotlib.pyplot as plt

import pymagnitude

m_path = "/Users/dreamflyer/Downloads/glove-lemmatized.6B.300d.magnitude"
#m_path = "/Users/dreamflyer/Downloads/glove.6B.50d.magnitude"

vectors = pymagnitude.Magnitude(m_path)

FIELDNAMES = ['ID', 'Text', 'Pronoun', 'Pronoun-offset', 'A', 'A-offset', 'A-coref', 'B', 'B-offset', 'B-coref', 'URL']

def save_obj(path, id, obj):
    full_path = os.path.join(path, id + ".data")

    with open(full_path, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


reader = PReader("/Users/dreamflyer/Downloads/gap-coreference-master/gap-development.tsv", "wiki")

def write_wiki(root, id, reader):
    item = reader.item(id)

    url = item['URL']

    title = url[url.rindex("/") + 1:]

    title = urllib.parse.unquote(title)

    try:
        page = wikipedia.WikipediaPage(title)

        data = {
            "title": page.title,
            "content": page.content
        }

        save_obj(root, id, data)
    except:
        print("failure")

# def read_wiki(root, id, reader):
#     item = reader.item(id)
#
#     url = item['URL']
#
#     title = url[url.rindex("/") + 1:]
#
#     page = wikipedia.WikipediaPage(title)
#
#     data = {
#         "title": page.title,
#         "content": page.content
#     }
#
#     save_obj(root, id, data)

c_a = 0
c_b = 0

c_a_true = 0
c_b_true = 0

c_a_false = 0
c_b_false= 0

items = [it for it in reader.ids if os.path.exists("wiki/" + it + ".data")]

a_hist = []
b_hist = []

l = len(items)

l2 = 2 * l

pn_true = 0

pn_false = 0

def filter(token):
    for item in ['#', '$', '@', '&', '*', '.', ',', '-', "=", ')', '(', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', "'", '"']:
        if item in token:
            return False

    return True


def stoa(sentence):
    return [s for s in nltk.word_tokenize(sentence) if filter(s)]

def tokenize(text):
    result = []

    sents = nltk.sent_tokenize(text)

    for item in sents:
        result.append(stoa(item))

    return result

def is_about(target, sentence):
    return target[0] in sentence

def cleanup(target, sentence):
    return [item for item in sentence if not (item in target)]

def intersect(s1, s2):
    return cleanup(s2, s1), cleanup(s1, s2)

def collect(target, sentences):
    abouts = [cleanup(target, item) for item in sentences if is_about(target, item)]
    #abouts = [item for item in sentences if is_about(target, item)]

    return [item for item in abouts if len(item) > 0]

def nearest(a1, a2):
    #a1, a2 = intersect(s1, s2)

    count = 0

    total = 0

    for item in a1:
        n = vectors.most_similar_to_given(item, a2)

        total += vectors.distance(item, n)

        count += 1

    for item in a2:
        n = vectors.most_similar_to_given(item, a1)

        total += vectors.distance(item, n)

        count += 1

    return total / count

def is_similar(s1, s2):
    return len(set(s1).intersection(s2)) == len(s1) and len(set(s2).intersection(s1)) == len(s2)

def remove_similars(target, sentences):
    result = []

    for item in sentences:
        for t in target:
            if is_similar(t, item):
                continue

            result.append(item)

    return result


def flatten(items_):
    result = []

    items = items_

    if len(items) > 5:
        items = items[:5]

    for item in items:
        for word in item:
            result.append(word)

    return result

a_a = []
a_b = []
b_a = []
b_b = []

for item in tqdm.tqdm(items, leave=True):
    rec = reader.item(item, True)

    A = "" + rec['A'].lower()
    B = "" + rec['B'].lower()

    isa = rec['A-coref'] == 'TRUE'
    isb = rec['B-coref'] == 'TRUE'

    a_tokens = stoa(A)
    b_tokens = stoa(B)

    pronoun = "" + rec['Pronoun'].lower()

    if len(a_tokens) ==0 or len(b_tokens) == 0:
        continue

    sample_sents = tokenize(rec['Text'].lower())
    wiki_sents = tokenize(rec['wiki_content'].lower())

    a_about_wiki = collect(a_tokens, wiki_sents)
    b_about_wiki = collect(b_tokens, wiki_sents)

    a_about_sample = collect(a_tokens, sample_sents)
    b_about_sample = collect(b_tokens, sample_sents)

    a_about_wiki = remove_similars(a_about_sample, a_about_wiki)
    b_about_wiki = remove_similars(b_about_sample, b_about_wiki)

    if len(a_about_wiki) ==0 or len(b_about_wiki) == 0:
        continue

    n_a_a = nearest(flatten(a_about_sample), flatten(a_about_wiki))
    n_a_b = nearest(flatten(a_about_sample), flatten(b_about_wiki))
    n_b_a = nearest(flatten(b_about_sample), flatten(a_about_wiki))
    n_b_b = nearest(flatten(b_about_sample), flatten(b_about_wiki))

    a_a.append(n_a_a)
    a_b.append(n_a_b)
    b_a.append(n_b_a)
    b_b.append(n_b_b)

print(sum(a_a) / len(a_a))
print(sum(a_b) / len(a_b))
print(sum(b_a) / len(b_a))
print(sum(b_b) / len(b_b))

plt.hist(a_a, bins='auto')
plt.title("n_a_a")
plt.show()

plt.hist(a_b, bins='auto')
plt.title("n_a_b")
plt.show()

plt.hist(b_a, bins='auto')
plt.title("n_b_a")
plt.show()

plt.hist(b_b, bins='auto')
plt.title("n_b_b")
plt.show()

    # if a > 30:
    #     a = 30
    #
    # if b > 30:
    #     b = 30

    # a_hist.append(a)
    #
    # b_hist.append(b)

# print("TOTAL")
#
# print((c_a + c_b) / l2)
#
# print("TRUE")
#
# print((c_a_true + c_b_true) / l2)
#
# print("FALSE")
#
# print((c_a_false + c_b_false)/ l2)
#
# print("P TRUE")
#
# print((pn_true)/ l2)
#
# print("P FALSE")
#
# print((pn_false)/ l2)
#
# plt.hist(a_hist, bins='auto')
#
# plt.show()
#
# plt.hist(b_hist, bins='auto')
#
# plt.show()
    #print(content.count(A))

    #print(item + ": " + rec["title"])

#write_wiki("wiki", reader.ids[12], reader)

# it = reader.item(reader.ids[12])
#
# print()

# ids = reader.ids
#
# it = reader.item(ids[10])
#
# url = "" + it['URL']
#
# #a = requests.get(url, {"action": "info"})
#
# title = url[url.rindex("/") + 1:]
#
# page = wikipedia.WikipediaPage(title)
#
# print(page.title)
#
# print(page.content)