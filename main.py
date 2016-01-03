import StringIO
import json
import logging
import random
import urllib
import urllib2
import ConfigParser

# for sending images
from PIL import Image
import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

# pozo functions
import pozo

# read configuration
config = ConfigParser.ConfigParser()
config.read('pozo.cfg')

# global constants (read from configuration file)
# Base telegram bot URL
BASE_URL = 'https://api.telegram.org/bot' + config.get('telegram', 'TOKEN', 0) + '/'
# allowed chats
ALLOWED_CHATS = config.get('chat', 'ALLOWED_IDS').split(',')
# max API tries
MAX_TRIES = 16
# Bot name
BOT_NAME = config.get('telegram', 'NAME')

# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        message = body['message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id))
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        def wrongCommand():
            reply(pozo.getWrongCommand() + ' ' + u'\U0001F621')

        # Comment these lines if you want your bot to interact with everyone
        if not str(chat_id) in ALLOWED_CHATS:
            reply('You (ID: {}) have no power here '.format(str(chat_id)) + u'\U0001F605')
            return

        # Enable bot
        if (text == '/start') or (text == '/start@'+BOT_NAME):
            reply('PozoBot enabled ' + u'\U0001F60F')
            pozo.setEnabled(chat_id, True)
        # Disable bot
        elif (text == '/stop') or (text == '/stop@'+BOT_NAME):
            reply('PozoBot disabled ' + u'\U0001F632')
            pozo.setEnabled(chat_id, False)
        # Commands
        elif pozo.getEnabled(chat_id):
            try:
                if (text == '/help') or (text == 'help@'+BOT_NAME):
                    reply(pozo.commandsHelp())
                elif text.startswith('/add '):
                    subreddit = text[len('/add '):].rsplit('@'+BOT_NAME, 1)[0]
                    pozo.addSubreddit(chat_id, subreddit)
                    reply('Subreddit {} added'.format(subreddit))
                elif (text == '/list') or (text == '/list@'+BOT_NAME):
                    feed_list = pozo.getSubreddits(chat_id)
                    if not feed_list:
                        reply('No subscriptions yet')
                    else:
                        reply('Subscriptions:\n\n'+'\n'.join(feed_list))
                elif text.startswith('/del '):
                    subreddit = text[len('/del '):].rsplit('@'+BOT_NAME, 1)[0]
                    pozo.delSubreddit(chat_id, subreddit)
                    reply('Subreddit {} deleted'.format(subreddit))
                elif (text == '/delall') or (text == '/delall@'+BOT_NAME):
                    pozo.delAllSubreddits(chat_id)
                    reply('All subscriptions deleted')
                elif (text == '/pozo') or (text == '/pozo@'+BOT_NAME):
                    reply(img=pozo.getRandomImg(chat_id, MAX_TRIES))
                elif text.startswith('/pozo '):
                    subreddit = text[len('/pozo '):].rsplit('@'+BOT_NAME, 1)[0]
                    reply(img=pozo.getSubredditImg(chat_id, subreddit, MAX_TRIES))
                elif text.startswith('/'):
                    wrongCommand()
            except ValueError as e:
                reply(str(e))
            except Exception:
                reply('... sorry, I\'m useless right now ' + u'\U0001F625')

app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
