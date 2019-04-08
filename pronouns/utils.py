import nltk

def filter(token):
    for item in ['#', '$', '@', '&', '*', '.', ',', '-', "=", ')', '(', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', "'", '"']:
        if item in token:
            return False

    return True

def flatten(items_):
    result = []

    items = items_

    for item in items:
        for word in item:
            result.append(word)

    return result

def stoa_1(sentence):
    return nltk.word_tokenize(sentence)

def stoa(sentence):
    return [s for s in nltk.word_tokenize(sentence) if filter(s)]

def tokenize(text):
    result = []

    sents = nltk.sent_tokenize(text)

    for item in sents:
        result.append(stoa(item))

    return result