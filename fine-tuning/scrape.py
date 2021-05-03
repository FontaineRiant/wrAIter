import twitter
import json
import codecs
import praw


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


