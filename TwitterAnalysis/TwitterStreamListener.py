import tweepy
import yaml
import json
import sqlite3
from TweetHandler import TweetHandler


class TwitterStreamListener(tweepy.StreamListener):
    def __init__(self):
        db_info = yaml.safe_load(open("config/db.yml"))
        conn = sqlite3.connect(db_info["database_name"])
        self.tweet_handler = TweetHandler(conn)

    def on_data(self, data):
        try:
            json_data = json.loads(data)

            self.tweet_handler.save_tweet(json_data)
            return True
        except KeyError as k:
            pass

    def on_error(self, status_code):
        if status_code == 403:
            print("Limit is maybe reached")
