import tweepy
import json
from TweetHandler import TweetHandler


class TwitterStreamListener(tweepy.StreamListener):
    def __init__(self):
        # grab db info
        self.tweet_handler = TweetHandler()

    def on_data(self, data):
        # TODO properly handle exceptions
        try:
            json_data = json.loads(data)

            self.tweet_handler.save_tweet(json_data)
            return True
        except KeyError as k:
            print(k)
            return True

    def on_error(self, status_code):
        # TODO properly handle http errors
        if status_code == 403:
            print("Limit is maybe reached")

