import pandas as pd
import os
import random

def annotate_tweet(tweet_id, company_tweets):
    ''' 
    Category : 0 if complain, 1 if question, 2 if simple mention without
                expectation of an answer
    Toxicity: 0 if neutral, 1 if slighly aggressive, 2 if foul and 
            aggressive, 3 if insult but request, 4 if full insult
    Intent: str expected, main intent of the tweet (eg: retard, prix) (unique)
    Entities: str, entities are separated by spaces
    '''
    print(company_tweets[company_tweets.id == tweet_id].text.values[0])

    categ = int(input('Category:\n'))
    while categ not in [0, 1, 2]:
        categ = int(input('Category: 0 if complain, 1 if question, 2 if mention\n'))
        
    if categ != 2:  # if the tweet is only a mention, we don't annotate it
        
        tox = input('Toxicity:\n')
        toxicity = int(tox) if isinstance(tox, int) else 0  # default is 0
        while toxicity not in [0, 1, 2, 3, 4]:
            toxicity = int(input('Toxicity: level from 0 (not toxic) to 4 (very toxic)\n'))
    
        intent = input('Intention:\n').lower()
        while len(intent.split(' ')) > 1:
            intent = input('Intention: unique main intent of the tweet\n').lower()
    
        entities = input('Entities:\n').lower().split(' ')

    else:
        toxicity, intent, entities = [-1, -1, -1]
        
    return {'tweet_id': tweet_id, 
            'category': categ,
            'toxicity': toxicity,
            'intent': intent,
            'entities': entities}

def annotate_csv(company):
    '''
    Annotate multiple tweets for a single company
    '''
    if company + '_annotations.csv' in os.listdir('annotations'):
        company_annotations = pd.read_csv(os.path.join('annotations', 
                                                       company + '_annotations.csv'))
    else:
        company_annotations = pd.DataFrame(columns=['tweet_id', 'company', 
                                                    'category', 'toxicity', 
                                                    'intent', 'entities'])
    
    company_tweets = pd.read_csv(os.path.join('data', company + '.csv'))
    
    stop = False
    annotations_to_append = list()
    while stop == False:
        potential_ids = set(company_tweets.id.values) - set(company_annotations.tweet_id.values)
        tweet_id = random.choice(list(potential_ids))
        tweet_annot = annotate_tweet(tweet_id, company_tweets)
        tweet_annot['company'] = company
        annotations_to_append.append(tweet_annot)
        
        stop = bool(input('Continue?'))
    
    temp_df_to_concat = pd.DataFrame(annotations_to_append)
    company_annotations = pd.concat([company_annotations, temp_df_to_concat], 
                                    sort=False)
    
    company_annotations.to_csv(os.path.join('annotations', company + '_annotations.csv'), 
                               index=False)
    return 1
