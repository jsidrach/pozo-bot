# Telegram Helpers
import TelegramHelpers as Telegram

# Read configuration file
import ConfigParser

# Webhook
import webapp2

# Random image from subreddit
import Pozo

# Read configuration
config = ConfigParser.ConfigParser()
config.read('pozo.cfg')

# Global constants (read from configuration file)
# Base telegram bot URL
BASE_URL = 'https://api.telegram.org/bot' + config.get('telegram', 'TOKEN', 0) + '/'
# Bot name
BOT_NAME = config.get('telegram', 'NAME')

# Request handler via Webhook
class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        # Obtain command
        (text, metadata) = Telegram.GetCommand(self)

        # Commands
        try:
            if (text == '/help') or (text == 'help@'+BOT_NAME):
                Telegram.ReplyWith(metadata, msg=Pozo.HELP_COMMAND)
            elif text.startswith('/add '):
                subreddit = text[len('/add '):].rsplit('@'+BOT_NAME, 1)[0]
                Pozo.AddSubreddit(metadata['chat_id'], subreddit)
                Telegram.ReplyWith(metadata, msg='Subreddit {} added'.format(subreddit))
            elif (text == '/list') or (text == '/list@'+BOT_NAME):
                feed_list = Pozo.GetSubreddits(metadata['chat_id'])
                if not feed_list:
                    Telegram.ReplyWith(metadata, msg='No subscriptions yet')
                else:
                    Telegram.ReplyWith(metadata, msg='Subscriptions:\n\n'+'\n'.join(feed_list))
            elif text.startswith('/del '):
                subreddit = text[len('/del '):].rsplit('@'+BOT_NAME, 1)[0]
                Pozo.DelSubreddit(metadata['chat_id'], subreddit)
                Telegram.ReplyWith(metadata, msg='Subreddit {} deleted'.format(subreddit))
            elif (text == '/delall') or (text == '/delall@'+BOT_NAME):
                Pozo.DelAllSubreddits(metadata['chat_id'])
                Telegram.ReplyWith(metadata, msg='All subscriptions deleted')
            elif (text == '/pozo') or (text == '/pozo@'+BOT_NAME):
                (image, extension) = Pozo.GetRandomImg(metadata['chat_id'])
                metadata['extension'] = extension
                Telegram.ReplyWith(metadata, img=image)
            elif text.startswith('/pozo '):
                subreddit = text[len('/pozo '):].rsplit('@'+BOT_NAME, 1)[0]
                (image, extension) = Pozo.GetRandomImg(metadata['chat_id'], subreddit)
                metadata['extension'] = extension
                Telegram.ReplyWith(metadata, img=image)
            elif text.startswith('/'):
                Telegram.ReplyWith(metadata, msg='Wrong command ' + u'\U0001F621')
        except Exception as e:
            Telegram.ReplyWith(metadata, msg=str(e))

# Set handlers
app = webapp2.WSGIApplication([
    ('/me', Telegram.MeHandler),
    ('/updates', Telegram.GetUpdatesHandler),
    ('/set_webhook', Telegram.SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
