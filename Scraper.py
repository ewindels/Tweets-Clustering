import pandas as pd
import twitter
import re
import json
import os
from time import sleep

with open('credentials.json') as handle:
    credentials = json.loads(handle.read())

api = twitter.Api(consumer_key=credentials['consumer_key'],
                  consumer_secret=credentials['consumer_secret'],
                  access_token_key=credentials['access_token_key'],
                  access_token_secret=credentials['access_token_secret'],
                  tweet_mode='extended')

with open('companies.json') as handle:
    companies = json.loads(handle.read())


def get_tweets(company, id_=0, time='newest', mode='to'):
    company_account = companies[company]
    if mode == 'to':
        query = '%40{}%20-filter%3Aretweets%20-filter%3Areplies'.format(company_account)
        count = 100
        if time == 'oldest':
            return api.GetSearch(raw_query="q={}&max_id={}&lang=fr&count={}".format(query, id_, count),
                                 result_type='recent')
        elif time == 'newest':
            return api.GetSearch(raw_query="q={}&since_id={}&lang=fr&count={}".format(query, id_, count),
                                 result_type='recent')
        elif time == 'new_company':
            return api.GetSearch(raw_query="q={}&lang=fr&count={}".format(query, count), result_type='recent')
    elif mode == 'from':
        query = 'from%3A{}%20-filter%3Aretweets%20filter%3Areplies'.format(company_account)
        count = 100
        if time == 'oldest':
            return api.GetSearch(raw_query="q={}&max_id={}&lang=fr&count={}".format(query, id_, count),
                                 result_type='recent')
        elif time == 'newest':
            return api.GetSearch(raw_query="q={}&since_id={}&lang=fr&count={}".format(query, id_, count),
                                 result_type='recent')
        elif time == 'new_company':
            return api.GetSearch(raw_query="q={}&lang=fr&count={}".format(query, count), result_type='recent')


def filter_img(text):
    return re.sub(r'https://t.co/\w+', '[LIEN]', text)


def create_new_data(tweets, mode='to'):
    new_data = pd.DataFrame()
    new_data['id'] = [tweet.id for tweet in tweets]
    new_data['text'] = [filter_img(tweet.full_text) for tweet in tweets]
    new_data['data'] = [tweet.created_at for tweet in tweets]
    new_data['user'] = [tweet.user.name for tweet in tweets]
    new_data['user_id'] = [tweet.user.id for tweet in tweets]
    new_data['favorite_cnt'] = [tweet.favorite_count for tweet in tweets]
    new_data['retweet_cnt'] = [tweet.retweet_count for tweet in tweets]
    if mode == 'from':
        new_data['reply_to_id'] = [tweet.in_reply_to_status_id for tweet in tweets]
    return new_data


def update_data(company, time='newest', mode='to'):
    """
    Supported times are newest, oldest, and new_company
    Supported mode are to and from
    """
    if mode == 'to':
        if '{}.csv'.format(company) in os.listdir('data'):
            data_df = pd.read_csv('data/{}.csv'.format(company))
        else:
            time = 'new_company'
            data_df = pd.DataFrame(columns=['id', 'text', 'data', 'user', 'user_id', 'favorite_cnt', 'retweet_cnt'])
        print('{:>5} tweets to {:<15}'.format(data_df.shape[0], company), end=' | ')
    elif mode == 'from':
        if '{}_replies.csv'.format(company) in os.listdir('data'):
            data_df = pd.read_csv('data/{}_replies.csv'.format(company))
        else:
            time = 'new_company'
            data_df = pd.DataFrame(columns=['id', 'text', 'data', 'user', 'user_id', 'favorite_cnt', 'retweet_cnt',
                                            'reply_to_id'])
        print('{:>5} tweets from {:<15}'.format(data_df.shape[0], company), end=' | ')
    else:
        print('Mode does not exist')
        return 1

    if time == 'newest':
        new_tweets = list()
        id_ = data_df['id'].max() + 1
        while True:
            tweets = get_tweets(company, id_, time, mode)
            if len(tweets) > 0:
                new_tweets.extend(tweets)
                id_ = max([tweet.id for tweet in tweets]) + 1
            else:
                break
    elif time == 'oldest':
        new_tweets = list()
        id_ = data_df['id'].min() - 1
        while True:
            tweets = get_tweets(company, id_, time, mode)
            if len(tweets) > 0:
                new_tweets.extend(tweets)
                id_ = min([tweet.id for tweet in tweets]) - 1
            else:
                break
    elif time == 'new_company':
        id_ = 0
        new_tweets = get_tweets(company, id_, time, mode)
        if len(new_tweets) > 0:
            id_ = min([tweet.id for tweet in new_tweets]) - 1
            while True:
                time = 'oldest'
                tweets = get_tweets(company, id_, time, mode)
                if len(tweets) > 0:
                    new_tweets.extend(tweets)
                    id_ = min([tweet.id for tweet in tweets]) - 1
                else:
                    break
    else:
        print('Time does not exist')
        return 1
    new_data = create_new_data(new_tweets)
    print('{:>4} new tweets'.format(len(new_tweets)))

    if new_data.shape[0] > 0:
        new_data_df = pd.concat([data_df, new_data])
        if mode == 'to':
            new_data_df.to_csv('data/{}.csv'.format(company), index=False)
        elif mode == 'from':
            new_data_df.to_csv('data/{}_replies.csv'.format(company), index=False)
        return 0
    else:
        return 1


def update_all(mode='to'):
    for company in sorted(companies):
        update_data(company, 'newest', mode)
        sleep(1)


def check_all_companies():
    total_to = 0
    total_from = 0
    for company in sorted(companies):
        data_df_to = pd.read_csv('data/{}.csv'.format(company))
        data_df_from = pd.read_csv('data/{}_replies.csv'.format(company))
        print('{:<15} : {:>4} tweets to | {:>4} tweets from'.format(company, data_df_to.shape[0],
                                                                    data_df_from.shape[0]))
        total_to += data_df_to.shape[0]
        total_from += data_df_from.shape[0]
    print('\nTotal: {} tweets to | {} tweets from'.format(total_to, total_from))

