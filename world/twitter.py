import collections
import tweepy
from django.conf import settings


class Twitter(object):
    def __init__(self):
        auth = tweepy.OAuthHandler(settings.TW_CONSUMER_KEY, settings.TW_CONSUMER_SECRET)
        auth.set_access_token(settings.TW_TOKEN, settings.TW_TOKEN_SECRET)
        self.t = tweepy.API(auth)

    def tsearch(self, keyword):
        tweets = collections.deque()
        results = self.t.search(keyword)
        count = 0
        for result in results:
            temp = Tweet()
            temp.stamp = dateutil.parser.parse(result._json['created_at'])
            temp.username = result._json['user']['screen_name']
            temp.fullname = result._json['user']['name']
            temp.client = Markup(result._json['source'])
            temp.text = result._json['text']
            temp.count = count
            for urls in result._json['entities']['urls']:
                temp.urls.append(urls['url'])
            tweets.append(temp)
            count += 1
            del temp
        return tweets

    def trends(self):
        tr = self.trends_place(2358820)
        tr = tr[0]['trends']
        z = []
        for trend in tr:
            z.append(trend['name'])
        return (z)


class Tweet(object):
    def __init__(self):
        self.count = 0
        self.username = u'@username'
        self.fullname = u'User Name'
        self.client = u'Python 3.x'
        self.stamp = datetime.datetime.now()
        self.text = u'He sings in the treetop, all day long.'
        self.urls = []
