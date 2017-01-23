class TweetHandler:
    def __init__(self, conn):
        # init sql connection
        self.conn = conn
        self.cursor = self.conn.cursor()

    def save_tweet(self, tweet):
        """
        Save the tweet to the database
        """
        self.cursor.execute(
            "INSERT INTO tweet_data VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (tweet["id_str"], tweet["text"], tweet["created_at"],
             tweet["favorite_count"], tweet["lang"], tweet["retweet_count"],
             tweet["coordinates"], 0))
        self.conn.commit()

    def filter_tweet(tweet):
        """
        Function that will decide what tweets to actually save
        TODO decide how to filter tweets and actually use this function
        """
        return True
