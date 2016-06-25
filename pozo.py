# Basic libraries
import random
import json
import re
import urllib
import urllib2
import logging

# Google App Engine
from google.appengine.api import urlfetch
from google.appengine.ext import ndb

# Constants
# Help command
HELP_COMMAND = ('The almighty @PozoBot!\n\nCommands available:\n' \
                '/help - For n00bs\n' \
                '/list - List subscriptions\n' \
                '/add <id> - Subscribe to a subreddit\n' \
                '/del <id> - Delete subscription to a subreddit\n' \
                '/delall - Delete all subscriptions\n' \
                '/pozo - Get a random image from a random subscription\n' \
                '/pozo <id> - Get a random image from a given subreddit\n\n' \
                '... and that\'s all, folks! ' + u'\U0001F601')
# Maximum number of tries before giving up
MAX_TRIES = 5
# Base URL of Reddit
BASE_URL = 'https://reddit.com/r/'
# File extension of Reddit requests
END_URL = '/random/.json'

# Timeout for fetch
urlfetch.set_default_fetch_deadline(60)

#
# Reddit functions
#

# Add subscription
def AddSubreddit(chat_id, subreddit):
    sf = __SubredditFeeds.get_or_insert(chat_id)
    if not subreddit in sf.subreddit_feeds:
        sf.subreddit_feeds.append(subreddit)
        sf.put()

# Get list of subscriptions
def GetSubreddits(chat_id):
    sf = __SubredditFeeds.get_or_insert(chat_id)
    return sf.subreddit_feeds

# Delete subscription
def DelSubreddit(chat_id, subreddit):
    sf = __SubredditFeeds.get_or_insert(chat_id)
    sf.subreddit_feeds = [x for x in sf.subreddit_feeds if x != subreddit]
    sf.put()

# Delete all subscriptions
def DelAllSubreddits(chat_id):
    sf = __SubredditFeeds.get_or_insert(chat_id)
    sf.subreddit_feeds[:] = []
    sf.put()

# Get a random image from subscriptions
def GetRandomImg(chat_id, subreddit=None, tries=MAX_TRIES):
    sf = __SubredditFeeds.get_or_insert(chat_id)
    if not sf.subreddit_feeds and subreddit is None:
        raise ValueError('No feeds yet')
    if tries <= 0:
        raise ValueError('Empty gallery')

    try:
        subreddit_chosen = random.choice(sf.subreddit_feeds) if subreddit is None else subreddit
        random_post = json.loads(urlfetch.Fetch(BASE_URL + subreddit_chosen + END_URL).content)
        img_url = random_post[0]['data']['children'][0]['data']['url']

        extension = __get_extension(img_url)
        if not extension:
            return GetRandomImg(chat_id, subreddit, tries-1)

        return (urlfetch.Fetch(img_url).content, extension)

    except Exception, e:
        logging.warning(repr(e))
        return GetRandomImg(chat_id, subreddit, tries-1)

# Return the extension of the image
def __get_extension(url):
    return '.' + url.encode('utf8').split('.')[-1].lower() if re.match(r'(?i)^.*\.(tif|jpeg|jpg|png|bmp)$', url) else None

# Storage of subscriptions
class __SubredditFeeds(ndb.Model):
    # Key name: chat_id (string)
    subreddit_feeds = ndb.StringProperty(repeated=True)
