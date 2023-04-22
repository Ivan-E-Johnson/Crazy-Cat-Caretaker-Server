from time import time


class Camera(object):
    default = open("static/play.png", "rb").read()
    feeds = {}

    @staticmethod
    def delete_feed(video_key):
        if video_key in Camera.feeds:
            del Camera.feeds[video_key]

    def __init__(self, feed_key):
        self.feed_key = feed_key

    def get_frame(self):
        return (
            Camera.feeds[self.feed_key]
            if self.feed_key in Camera.feeds
            else Camera.default
        )
