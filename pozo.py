import StringIO
import json
import logging
import random
import urllib
import urllib2
import ConfigParser
import sys
sys.path.insert(0, 'libs')
import requests

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from google.appengine.ext import db
import webapp2

# definitions
WRONG_COMMAND = [
                    'Your command is wrong and you should feel bad about it',
                    'You useless bastard, learn how to use me before trying again',
                    'You can\'t fool me with your bad syntax',
                    'Error, user is stupid',
                    'Sorry, I can\'t fix your stupid spelling mistake',
                    'Take time and rethink that before submitting again',
                    'Wrong command - It\'s ok, shit happens',
                    'How are you even allowed in this group? Please, submit a valid query',
                    'I\'d rather suicide than continue listening your bad queries',
                    'Bad input - we are all in awe you are this incompetent',
                    'You said something with no meaning',
                    'You are as useful as nipples on a man',
                    'Your command doesn\'t make sense to me'
                ]


# configuration variables
# read configuration
config = ConfigParser.ConfigParser()
config.read('pozo.cfg')

# global constants (read from configuration file)
CLIENT_ID = config.get('imgur', 'CLIENT_ID', 0)
IMGUR_HEADER = 'Client-ID ' + CLIENT_ID
IMGUR_API = 'https://api.imgur.com/3/gallery/r/'

# ================================

# Defined string helpers
def getWrongCommand():
    return random.choice(WRONG_COMMAND)

def commandsHelp():
    return ('The almighty @PozoBot!\n\nCommands available:\n'+
              '/help - For n00bs\n'+
              '/add <id> - Subscribe to a subreddit\n'+
              '/del <id> - Delete subscription to a subreddit\n'+
              '/delall - Delete all subscriptions\n'+
              '/pozo - Get a random image from a random subscription'
              '/pozo <id> - Get a random image from a given subreddit\n\n'+
              '... and that\'s all, folks! ' + u'\U0001F601')

# ================================
# enable/disable the bot
class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False

# ================================
# store a image temporary
#   (one maximum for each chat_id)
class TempImage(ndb.Model):
    # key name: str(chat_id)
    temp_image = ndb.BlobProperty()

def setTempImage(chat_id, img_url):
    ti = TempImage.get_or_insert(str(chat_id))
    ti.temp_image = db.Blob(urlfetch.Fetch(img_url).content)
    ti.put()

def getTempImage(chat_id):
    ti = TempImage.get_or_insert(str(chat_id))
    if ti:
        return ti.temp_image


# ================================
# subreddit galleries functions

# storage of subscriptions
class SubredditFeeds(ndb.Model):
    # key name: str(chat_id)
    subreddit_feeds = ndb.StringProperty(repeated=True)

# add subscription
def addSubreddit(chat_id, subreddit):
    sf = SubredditFeeds.get_or_insert(str(chat_id))
    if not subreddit in sf.subreddit_feeds:
        sf.subreddit_feeds.append(subreddit)
        sf.put()

# delete subscription
def delSubreddit(chat_id, subreddit):
    sf = SubredditFeeds.get_or_insert(str(chat_id))
    sf.subreddit_feeds = [x for x in sf.subreddit_feeds if x != subreddit]
    sf.put()

# delete all subscriptions
def delAllSubreddits(chat_id):
    sf = SubredditFeeds.get_or_insert(str(chat_id))
    sf.subreddit_feeds[:] = []
    sf.put()

# get a random image from subscriptions
def getRandomImg(chat_id):
    sf = SubredditFeeds.get_or_insert(str(chat_id))
    if not sf.subreddit_feeds:
        raise ValueError('No feeds yet')
    try:
        results = requests.get(IMGUR_API + random.choice(sf.subreddit_feeds), headers={'Authorization': IMGUR_HEADER})
        data = results.json()['data']
        img_url = random.choice(data)['link']
        setTempImage(chat_id, img_url)
        return img_url
    except ValueError:
        raise ValueError('Empty gallery')

# get a random image from a given subreddit
def getSubredditImg(chat_id, subreddit):
    try:
        results = requests.get(IMGUR_API + subreddit, headers={'Authorization': IMGUR_HEADER})
        data = results.json()['data']
        img_url = random.choice(data)['link']
        setTempImage(chat_id, img_url)
        return img_url
    except ValueError:
        raise ValueError('Empty gallery')
