import os.path
import json
import urllib2


class HackerNews (object):
    def get_stories (self):
        url = 'http://timdavi.es/hackernews/'
        data = urllib2.urlopen(url).read()
        return json.loads(data)

if __name__ == '__main__':
    a = HackerNews()
    data = a.get_stories()