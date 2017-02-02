from Trainer import sentiment


class TweetHandler:
    def __init__(self, conn):
        # init sql connection
        self.conn = conn
        self.cursor = self.conn.cursor()

    def save_tweet(self, tweet):
        """
        Save the tweet to the database
        """
        sentiment_value, confidence = sentiment(tweet["text"])
        if self.filter_tweet(tweet, confidence):
            print(tweet["text"])
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
