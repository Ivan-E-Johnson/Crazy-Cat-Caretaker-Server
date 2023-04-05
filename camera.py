from time import time


class Camera(object):
    feeds = {"TESTFEEDKEY": open("static/play.png", "rb").read()}

    def __init__(self):
        self.feed_key = "TESTFEEDKEY"

    def get_frame(self):
        return Camera.feeds[self.feed_key]
