from threading import Thread
from Trainer import sentiment
import yaml
import sqlite3
from queue import Queue

queue = Queue()


class TweetHandler():
    def __init__(self):
        # init sql connection
        TweetConsumer().start()

    def save_tweet(self, tweet):
        """
        Save the tweet to the database
        """
        queue.put(tweet)


class TweetConsumer(Thread):
    def __init__(self):
        # init sql connection
        super(TweetConsumer, self).__init__()
        self.db_name = yaml.safe_load(open("config/db.yml"))["database_name"]

    def run(self):
        global queue
        while True:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            data = queue.get()
            try:
                self.save_tweet(data)
            except KeyError:
                pass
            queue.task_done()

    def save_tweet(self, tweet):
        """
        Save the tweet to the database
        """
        sentiment_value, confidence = sentiment(tweet["text"])
        text = tweet["text"]
        if self.filter_tweet(tweet, confidence):
            print(text)
            print(confidence, ":", sentiment_value)
            self.cursor.execute(
                "INSERT INTO tweet_data VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (tweet["id_str"], tweet["text"], tweet["created_at"],
                 tweet["favorite_count"], tweet["lang"],
                 tweet["retweet_count"], tweet["coordinates"],
                 sentiment_value))
            self.conn.commit()

    def filter_tweet(self, tweet, confidence):
        """
        Function that will decide what tweets to actually save
        TODO decide how to filter tweets and actually use this function
        """
        return confidence > .8 and not tweet["text"].startswith(
            "RT") and tweet["lang"] == "en"
