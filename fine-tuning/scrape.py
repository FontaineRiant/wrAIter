import re
import time

import twitter
import json
import codecs
import praw
import requests
import gpt_2_simple as gpt2


def scrape_twitter(target_user_handle: str, exclude_replies: bool = False):
    # load config
    with open('settings.json') as json_config:
        config = json.load(json_config)

    # API authentification
    api = twitter.Api(consumer_key=config['twitter']['consumer_key'],
                      consumer_secret=config['twitter']['consumer_secret'],
                      access_token_key=config['twitter']['access_token_key'],
                      access_token_secret=config['twitter']['access_token_secret'],
                      sleep_on_rate_limit=True,
                      tweet_mode='extended')

    tweets = []
    oldest_tweet = None

    # get all tweets and replies from user
    print("Fetching tweets and replies by {} ".format(target_user_handle), end='')
    while True:
        response = api.GetUserTimeline(screen_name=target_user_handle, count=200, exclude_replies=exclude_replies,
                                       trim_user=True, include_rts=False, max_id=oldest_tweet)
        if len(response) == 0:
            print(' done.')
            break

        tweets.extend(response)
        oldest_tweet = tweets[-1].id - 1
        print('.', end='')

    # print to file
    with codecs.open('data/twitter_{}.txt'.format(target_user_handle), "w+", "utf") as out_file:
        for tweet in tweets:
            print(f"{tweet.full_text}\n", file=out_file)

    api.ClearCredentials()
    print("Tweets saved successfully.")


def scrape_reddit(username: str, exclude_comments=False):
    # load config
    with open('settings.json') as json_config:
        config = json.load(json_config)

    # API authentification
    reddit = praw.Reddit(client_id=config['reddit']['client_id'],
                         client_secret=config['reddit']['client_secret'],
                         user_agent=config['reddit']['user_agent'])

    print("Fetching reddit posts by {} ...".format(username), end='')
    with codecs.open('data/reddit_{}.txt'.format(username), "w+", "utf") as out_file:
        for post in reddit.redditor(username).submissions.new(limit=None):
            print(f"{post.title}", file=out_file)
            print(f"{post.selftext}\n", file=out_file)
        print(" done.")

        if not exclude_comments:
            print("Fetching reddit comments by {} ...".format(username), end='')
            for comment in reddit.redditor(username).comments.new(limit=None):
                print(f"{comment.body}\n", file=out_file)
            print(" done.")

        print("Reddit content saved successfully.")


def scrape_subreddit(subreddit: str, exclude_comments=False):
    # load config
    with open('settings.json') as json_config:
        config = json.load(json_config)

    # API authentification
    reddit = praw.Reddit(client_id=config['reddit']['client_id'],
                         client_secret=config['reddit']['client_secret'],
                         user_agent=config['reddit']['user_agent'])

    print("Fetching reddit posts from {} ...".format(subreddit), end='')
    with codecs.open('data/reddit_{}.txt'.format(subreddit), "w+", "utf") as out_file:
        for post in reddit.subreddit(subreddit).top(limit=None):
            print(f"{post.title}", file=out_file)
            print(f"{post.selftext}\n", file=out_file)
        print(" done.")

        if not exclude_comments:
            print("Fetching reddit comments from {} ...".format(subreddit), end='')
            for comment in reddit.subreddit(subreddit).comments(limit=None):
                print(f"{comment.body}\n", file=out_file)
            print(" done.")

        print("Reddit content saved successfully.")


def scrape_pushift(subreddit: str, comments=True, lower_character_limit=100, sample_limit=10000):
    type = 'comment' if comments else 'submission'
    print(f"Fetching reddit {type}s from r/{subreddit} ...")
    last_stamp = ''
    counter = 0

    with codecs.open(f'data/r_{subreddit}_{type}s.txt', "w+", "utf") as out_file:
        while True:
            url = f'https://api.pushshift.io/reddit/{type}/search?subreddit={subreddit}&size=500' \
                  f'&before={last_stamp}&fields={"body" if comments else "selftext"},created_utc'

            time.sleep(1)
            res = requests.get(url)
            tries = 1
            while res.status_code != 200:
                if tries > 5:
                    print('timeout')
                    return
                tries += 1
                time.sleep(1)
                res = requests.get(url)

            res.encoding = res.apparent_encoding
            j = json.loads(res.content)

            if len(j['data']) == 0:
                break

            last_stamp = str(j['data'][-1]['created_utc'])

            j['data'] = [v for v in j['data'] if ('body' if comments else 'selftext') in v]

            for body, stamp in [(c['body' if comments else 'selftext'], c['created_utc']) for c in j['data']]:
                body = re.sub(r"^.*?https?://.*?$", "", body, flags=re.MULTILINE)  # remove urls
                body = re.sub(r"^.*?&amp;#x200B;.*?$", "", body, flags=re.MULTILINE)  # remove weird reddit separator
                body = re.sub(r"^.*?&amp;nbsp;.*?$", "", body, flags=re.MULTILINE)  # remove weird reddit separator
                body = re.sub(r"( )\1+", " ", body)  # remove duplicate spaces
                body = re.sub(r"(\n)\1+", "\n", body)  # remove duplicate newlines
                body = re.sub(r"(?<=^) +", "", body, flags=re.MULTILINE)  # remove spaces after a newline
                if len(body) >= lower_character_limit:
                    counter += 1
                    print(f"<|startoftext|>{body}<|endoftext|>{stamp}\n", file=out_file)
                    if counter % 1000 == 0:
                        print(f'Progress: {counter}')

        print(f"Reddit {type}s saved successfully.")


#scrape_pushift('Eve', comments=False)
#scrape_pushift('Eve', comments=True)
scrape_pushift('shortstories', comments=False)
scrape_pushift('HFY', comments=False)
scrape_pushift('WritingPrompts', comments=True, lower_character_limit=1000)
