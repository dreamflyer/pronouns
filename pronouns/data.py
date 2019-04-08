import os

import csv

import pickle

FIELDNAMES = ['ID', 'Text', 'Pronoun', 'Pronoun-offset', 'A', 'A-offset', 'A-coref', 'B', 'B-offset', 'B-coref', 'URL']

def load_obj(path, id):
    full_path = os.path.join(path, id + ".data")

    if not os.path.exists(full_path):
        return {
            "title": None,
            "content": None
        }

    with open(full_path, 'rb') as f:
        return pickle.load(f)

def read_data(file_name):
    result = {}

    with open(file_name, 'rU') as f:
        reader = csv.DictReader(f, fieldnames=FIELDNAMES, delimiter='\t')

        for row in reader:
            result[row['ID']] = row

    return result

class DataReader:
    def __init__(self, file_name, wiki_path=None):
        if not wiki_path:
            self.wiki_path = os.path.join(os.path.dirname(__file__), "wiki")

        self.data = read_data(file_name)

        self.ids = [item for item in  self.data.keys() if not item == 'ID']

        self.wiki_path = wiki_path

    def get_ids(self):
        return [it for it in self.ids if os.path.exists(self.wiki_path + "/" + it + ".data")]

    def item(self, id, read_wiki=False):
        data = self.data[id]

        if read_wiki:
            wiki = load_obj(self.wiki_path, id)

            data["title"] = wiki["title"]

            data["wiki_content"] = wiki["content"]

        return data