import tweepy
import sys
from TwitterStreamListener import TwitterStreamListener
from Authentication import create_api


class TwitterStream:
    def __init__(self):
        api = create_api(
            wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        stream_listener = TwitterStreamListener()
        self.stream = tweepy.Stream(auth=api.auth, listener=stream_listener)

    def begin_stream(self, text="trump"):
        self.stream.filter(track=[text])


if __name__ == "__main__":
    twitter = TwitterStream()
    if(len(sys.argv) > 1):
        twitter.begin_stream(sys.argv[1])
    else:
        twitter.begin_stream()
