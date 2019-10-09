import pandas as pd
import os
import json
from random import choices, choice

with open('companies.json') as handle:
    companies = list(json.loads(handle.read()))


class Annotator:
    def __init__(self, company=None, annotator=None):
        self.company = company
        self.annotator = annotator
        self.annotations_single_tweet = {'id': list(),
                                         'tweet_category': list(),
                                         'toxicity': list(),
                                         'intent': list()}
        self.annotations_comp_tweets = {'id_1': list(),
                                        'id_2': list(),
                                        'similarity': list()}
        self.tweets = pd.read_csv(os.path.join('data', company + '.csv'))['id', 'text']
        if company + '_annotations_single.csv' in os.listdir('annotations'):
        self.company_annotations = {'single': pd.read_csv(os.path.join('annotations', company + '_annotations.csv'),
                                          sep=';') if company + '_annotations.csv'

    def annotate(self, annotation_type='single'):
        if annotation_type == 'single':
            pass

        elif annotation_type == 'comp':
            while True:
                tweet_1, tweet_2 = 1, 1

        else:
            print('Supported annotation types are "single" and "comp"')