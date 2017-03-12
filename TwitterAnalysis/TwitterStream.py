import tweepy
import sys
from TwitterStreamListener import TwitterStreamListener
from Authentication import create_api


class TwitterStream:
    def __init__(self):
        api = create_api(
            wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.stream_listener = TwitterStreamListener()
        self.stream = tweepy.Stream(
            auth=api.auth, listener=self.stream_listener)

    def begin_stream(self, text="trump"):
        self.running = True
        self.stream.filter(track=[text], async=True)

    def end_stream(self):
        self.stream.disconnect()


if __name__ == "__main__":
    twitter = TwitterStream()
    if (len(sys.argv) > 1):
        twitter.begin_stream(sys.argv[1])
    else:
        twitter.begin_stream()
