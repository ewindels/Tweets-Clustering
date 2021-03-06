import pandas as pd
import twitter
import re
import json
import os
from time import sleep
from datetime import datetime

with open(os.path.join('credentials', 'credentials_pe.json')) as handle:
    credentials_pe = json.loads(handle.read())

with open(os.path.join('credentials', 'credentials_ew.json')) as handle:
    credentials_ew = json.loads(handle.read())

with open('companies.json') as handle:
    companies = json.loads(handle.read())


def make_api(who):
    if who == 'pe':
        credentials = credentials_pe
    elif who == 'ew':
        credentials = credentials_ew
    else:
        return 1
    return twitter.Api(consumer_key=credentials['consumer_key'],
                       consumer_secret=credentials['consumer_secret'],
                       access_token_key=credentials['access_token_key'],
                       access_token_secret=credentials['access_token_secret'],
                       tweet_mode='extended')


def get_tweets(company, max_id=0, since_id=0, mode='to'):
    tweet_accounts = companies[company]
    if mode == 'to':
        tweet_accounts_q = '%20OR%20'.join(['%40' + account for account in tweet_accounts])
        query = '{}%20-filter%3Aretweets%20-filter%3Areplies%20'.format(tweet_accounts_q)
    elif mode == 'from':
        tweet_accounts_q = '%20OR%20'.join(['from%3A' + account for account in tweet_accounts])
        query = '{}%20filter%3Areplies%20'.format(tweet_accounts_q)
    else:
        return 1
    if max_id != 0:
        max_id_q = '&max_id=' + str(max_id)
    else:
        max_id_q = ''
    if since_id != 0:
        since_id_q = '&since_id=' + str(since_id)
    else:
        since_id_q = ''
    api = make_api('pe') if mode == 'to' else make_api('ew')
    return api.GetSearch(raw_query="q={}{}{}&lang=fr&count=100".format(query, since_id_q, max_id_q),
                         result_type='recent')


def filter_links(text):
    return re.sub(r'https://t.co/\w+', '[LIEN]', text)


def create_new_data(tweets, company, mode='to'):
    new_data = pd.DataFrame()
    new_data['id'] = [tweet.id for tweet in tweets]
    new_data['text'] = [filter_links(tweet.full_text) for tweet in tweets]
    new_data['date'] = [tweet.created_at for tweet in tweets]
    new_data['user'] = [tweet.user.name for tweet in tweets]
    new_data['user_id'] = [tweet.user.id for tweet in tweets]
    if mode == 'to':
        new_data['favorite_cnt'] = [tweet.favorite_count for tweet in tweets]
        new_data['retweet_cnt'] = [tweet.retweet_count for tweet in tweets]
    if mode == 'from':
        new_data['reply_to_id'] = [tweet.in_reply_to_status_id for tweet in tweets]
        df_to = pd.read_csv('data/{}.csv'.format(company))
        new_data = new_data.loc[new_data['reply_to_id'].isin(df_to['id'])]
    return new_data


def update_data(company, time='newest', mode='to'):
    """
    Supported times are newest, oldest, and new_company
    Supported mode are to and from
    """
    if mode == 'to':
        if time != 'new_company' and '{}.csv'.format(company) in os.listdir('data'):
            data_df = pd.read_csv('data/{}.csv'.format(company))
        else:
            time = 'new_company'
            data_df = pd.DataFrame(columns=['id', 'text', 'date', 'user', 'user_id', 'favorite_cnt', 'retweet_cnt'])
            data_df.to_csv('data/{}.csv'.format(company), index=False)
        print('{:>5} tweets to {:<22}'.format(data_df.shape[0], company), end=' | ')
    elif mode == 'from':
        if time != 'new_company' and '{}_replies.csv'.format(company) in os.listdir('data'):
            data_df = pd.read_csv('data/{}_replies.csv'.format(company))
        else:
            time = 'new_company'
            data_df = pd.DataFrame(columns=['id', 'text', 'date', 'user', 'user_id', 'favorite_cnt', 'retweet_cnt',
                                            'reply_to_id'])
            data_df.to_csv('data/{}_replies.csv'.format(company), index=False)
        print('{:>5} tweets from {:<20}'.format(data_df.shape[0], company), end=' | ')
    else:
        print('Mode does not exist')
        return 1

    if time == 'newest':
        new_tweets = list()
        id_ = data_df['id'].max() + 1
        tweets = get_tweets(company, max_id=0, since_id=id_, mode=mode)
        tweets = [tweet for tweet in tweets if tweet.id > id_]
        new_tweets.extend(tweets)
        max_id = 0
        if len(tweets) > 0:
            max_id = min([tweet.id for tweet in tweets]) - 1
        while len(tweets) == 100:
            tweets = get_tweets(company, max_id=max_id, since_id=id_, mode=mode)
            tweets = [tweet for tweet in tweets if tweet.id > id_]
            new_tweets.extend(tweets)
            if len(tweets) > 0:
                max_id = min([tweet.id for tweet in tweets]) - 1
    elif time == 'oldest':
        new_tweets = list()
        id_ = data_df['id'].min() - 1
        while True:
            tweets = get_tweets(company, max_id=id_, since_id=0, mode=mode)
            new_tweets.extend(tweets)
            if len(tweets) > 0:
                id_ = min([tweet.id for tweet in tweets]) - 1
            if len(tweets) < 100:
                break
    elif time == 'new_company':
        new_tweets = get_tweets(company, max_id=0, since_id=0, mode=mode)
        if len(new_tweets) == 100:
            id_ = min([tweet.id for tweet in new_tweets]) - 1
            while True:
                tweets = get_tweets(company, max_id=id_, since_id=0, mode=mode)
                new_tweets.extend(tweets)
                if len(tweets) > 0:
                    id_ = min([tweet.id for tweet in tweets]) - 1
                if len(tweets) < 100:
                    break
    else:
        print('Time does not exist')
        return 1
    new_data = create_new_data(new_tweets, company, mode)

    if new_data.shape[0] > 0:
        print('{:>4} new tweets'.format(new_data.shape[0]))

        new_data_df = pd.concat([data_df, new_data])
        if mode == 'to':
            new_data_df = new_data_df.drop_duplicates('user_id', keep='last')
            new_data_df = new_data_df.drop_duplicates('text', keep='first')
            new_data_df.to_csv('data/{}.csv'.format(company), index=False)
        elif mode == 'from':
            new_data_df.to_csv('data/{}_replies.csv'.format(company), index=False)
        return 0
    else:
        print('   -')
        return 1


def tweets_estimate(company, mode='to'):
    df_to = pd.read_csv('data/{}{}.csv'.format(company, '_replies'*(mode == 'from')))
    df_to.index = pd.to_datetime(df_to['date'])
    df_to['date'] = pd.to_datetime(df_to['date'])
    last_hour = (df_to.index.max().hour, df_to.index.max().minute)
    current_hour = (datetime.today().hour, datetime.today().minute)
    time_since_last = datetime.today() - df_to.index.max()
    hours = df_to['date'].apply(lambda t: (t.hour, t.minute))
    if last_hour <= current_hour:
        in_hours = df_to.loc[(last_hour <= hours) & (hours <= current_hour)]
    else:
        in_hours = df_to.loc[(last_hour <= hours) | (hours <= current_hour)]
    total_days = (df_to.index.max() - df_to.index.min()).days
    hours_mean = in_hours.resample('D')['text'].count().sum() / total_days
    days_mean = df_to.resample('D')['text'].count().sum() / total_days
    return time_since_last.days, round(days_mean * time_since_last.days + hours_mean)


def update_all(mode='to', scheduler=True):
    for company in sorted(companies):
        if scheduler:
            days_since_last, estimate = tweets_estimate(company)
            if not (days_since_last >= 2 or estimate > 50):
                continue
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


def add_company(company):
    update_data(company, 'new_company', 'to')
    update_data(company, 'new_company', 'from')
