# Basic libraries
import httplib
import mimetypes
import urlparse
import uuid
import json
import logging
import urllib
import urllib2

# Read configuration file
import ConfigParser

# Send images
from PIL import Image

# Telegram Helper functions
import TelegramHelpers as Telegram

# Google App Engine
from google.appengine.api import urlfetch
import webapp2

# Read configuration
config = ConfigParser.ConfigParser()
config.read('pozo.cfg')

# Global constants (read from configuration file)
# Base telegram bot URL
BASE_URL = 'https://api.telegram.org/bot' + config.get('telegram', 'TOKEN', 0) + '/'
# Deadline for fetches in seconds
FETCH_DEADLINE = 60

#
# Auxiliary Telegram classes and functions (DO NOT TOUCH)
#

class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(FETCH_DEADLINE)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))

class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(FETCH_DEADLINE)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))

def GetCommand(req):
    urlfetch.set_default_fetch_deadline(FETCH_DEADLINE)
    url = req.request.get('url')
    if url:
        req.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))

    urlfetch.set_default_fetch_deadline(60)
    body = json.loads(req.request.body)
    logging.info('Request body:')
    logging.info(body)
    req.response.write(json.dumps(body))

    #update_id = str(body['update_id'])
    try:
        message = body['message']
    except:
        message = body['edited_message']
    message_id = str(message.get('message_id'))
    #date = str(message.get('date'))
    text = message.get('text')
    #sender = message.get('from')
    chat = message['chat']
    chat_id = str(chat['id'])
    metadata = {'message_id': message_id, 'chat_id': chat_id}

    if not text:
        logging.info('No text')
        return (None, metadata)

    return (text, metadata)

def ReplyWith(metadata, msg=None, img=None):
    if msg:
        resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode(
            {
                'chat_id': metadata['chat_id'],
                'text': msg.encode('utf-8'),
                'disable_web_page_preview': 'true',
                'reply_to_message_id': metadata['message_id'],
            })).read()
    elif img:
        resp = __post_multipart(BASE_URL + 'sendPhoto',
            [
                ('chat_id', metadata['chat_id'])
            ],
            [
                ('photo', 'PozoBot-RandomImage' + metadata['extension'], img),
            ])
    else:
        logging.error('No message or image specified')
        resp = None

    logging.info('Send response:')
    logging.info(resp)

# Internal functions
def __post_multipart(url, fields, files):
    parts = urlparse.urlparse(url)
    scheme = parts[0]
    host = parts[1]
    selector = parts[2]
    content_type, body = __encode_multipart_formdata(fields, files)
    if scheme == 'http':
        h = httplib.HTTP(host)
    elif scheme == 'https':
        h = httplib.HTTPS(host)
    else:
        raise ValueError('unknown scheme: ' + scheme)
    h.putrequest('POST', selector)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.endheaders()
    h.send(body)
    errcode, errmsg, headers = h.getreply()
    return h.file.read()

def __encode_multipart_formdata(fields, files):
    LIMIT = '----------' + uuid.uuid4().hex
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + LIMIT)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + LIMIT)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % __get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + LIMIT + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % LIMIT
    return content_type, body

def __get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
