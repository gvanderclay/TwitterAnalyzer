import tweepy
from TwitterStreamListener import TwitterStreamListener
from Authentication import create_api


class TwitterStream:
    def __init__(self):
        api = create_api(
            wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        stream_listener = TwitterStreamListener()
        self.stream = tweepy.Stream(auth=api.auth, listener=stream_listener)

    def begin_stream(self):
        self.stream.filter(track=["trump"])


if __name__ == "__main__":
    twitter = TwitterStream()
    twitter.begin_stream()
