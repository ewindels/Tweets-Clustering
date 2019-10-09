import pandas as pd
import os
import json
from random import choices, choice

with open('companies.json') as handle:
    companies = list(json.loads(handle.read()))


class Annotator:
    def __init__(self, company=None):
        self.company = company
        self.tweets = pd.read_csv(os.path.join('data', company + '.csv'))[['id', 'text']]
        self.company_annotations = {'single': pd.read_csv(os.path.join('annotations', company + '_single.csv')),
                                    'comp': pd.read_csv(os.path.join('annotations', company + '_comp.csv'))}

    def annotate(self, annotation_type='single'):

        def annotate_tweet(tweet_id, mode='partial'):
            """
            Category : 0 if complain, 1 if question, 2 if simple mention without
                        expectation of an answer, 3 if thanks
            Toxicity: 0 if neutral, 1 if neutral but vulgar, 2 if vulgar and slightly
                    aggressive, 3 if vulgar and aggressive but request, 4 if full insult
            Intent: str expected, main intent of the tweet (eg: retard, prix) (unique)
            """
            print(self.tweets[self.tweets.id == tweet_id].text.values[0])

            cat = input('Category:\n')
            categories = cat if len(cat) > 0 else '2'

            if categories != '2':  # if the tweet is only a mention, we don't annotate it
                tox = input('Toxicity:\n')
                toxicity = tox if len(tox) > 0 else '0'  # default is 0

                if mode != 'partial':
                    intent = input('Intention:\n').lower()
                else:
                    intent = None

            else:
                toxicity = intent = None

            return {'tweet_id': tweet_id,
                    'category': categories,
                    'toxicity': toxicity,
                    'intent': intent}

        if annotation_type == 'single':
            potential_ids = set(self.tweets.id.values) - set(self.company_annotations['single'].tweet_id.values)
            stop = False
            annotations_to_append = list()
            while not stop:
                tweet_id_ = choice(list(potential_ids))
                tweet_annot = annotate_tweet(tweet_id_)
                annotations_to_append.append(tweet_annot)
                potential_ids.remove(tweet_id_)

                stop = bool(input('Continue?'))

            temp_df_to_concat = pd.DataFrame(annotations_to_append)
            print('{} new annotations'.format(temp_df_to_concat.shape[0]))
            company_annotations = pd.concat([self.company_annotations['single'], temp_df_to_concat])

            company_annotations.to_csv(os.path.join('annotations', self.company + '_single.csv'), index=False)

        elif annotation_type == 'comp':
            while True:
                tweet_1, tweet_2 = 1, 1

        else:
            print('Supported annotation types are "single" and "comp"')


