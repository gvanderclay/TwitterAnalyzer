import yaml
import tweepy


def create_api(**options):
    config = yaml.safe_load(open("config/twitter_creds.yml"))
    consumer_key = config["consumer"]["key"]
    consumer_secret = config["consumer"]["secret"]
    access_token = config["access"]["token"]
    access_secret = config["access"]["secret"]
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.secure = True
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth, **options)
    return api
