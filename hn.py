import os.path
import json
import urllib2


class HackerNews (object):
    def _api_call (self, path):
        url = 'http://api.ihackernews.com' + path
        data = urllib2.urlopen(url).read()
        return json.loads(data)
    
    def get_stories (self):
        data = self._api_call('/page?format=json')
        return data


if __name__ == '__main__':
    a = HackerNews()
    data = a.get_stories()