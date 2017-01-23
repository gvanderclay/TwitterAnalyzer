class TweetHandler:
    def __init__(self, conn):
        self.conn = conn
        self.cursor = self.conn.cursor()

    def save_tweet(self, tweet):
        print("INSERT INTO tweet_data VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              tweet["id_str"], tweet["text"], tweet["created_at"],
              tweet["favorite_count"], tweet["lang"], tweet["retweet_count"],
              tweet["coordinates"], 0)
        self.cursor.execute(
            "INSERT INTO tweet_data VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (tweet["id_str"], tweet["text"], tweet["created_at"],
             tweet["favorite_count"], tweet["lang"], tweet["retweet_count"],
             tweet["coordinates"], 0))
        self.conn.commit()

    def filter_tweet(tweet):
        return True
