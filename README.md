# PozoBot

Small Telegram bot that lets the user subscribe to imgur subreddit galleries to retrieve random images. Compatible with [Google App Engine](https://cloud.google.com/appengine/docs).

Tech
----

PozoBot uses a number of open source projects to work properly:

* [telebot](https://github.com/yukuku/telebot/) - Telegram Bot starter kit - base work for this project
* [requests](http://docs.python-requests.org/en/latest/) - HTTP library in python

License
-------
[MIT](LICENSE) - Feel free to use and edit.

Commands
--------
List of all available commands:
  * **/start** - enable the bot
  * **/stop** - disable the bot
  * **/help** - display help text
  * **/list** - list subscriptions
  * **/add _id_** - subscribe to a subreddit
  * **/del _id_** - delete subscription to a subreddit
  * **/delall** - delete all subscriptions
  * **/pozo** - get a random image from a random subscription
  * **/pozo _id_** - get a random image from a given subreddit

Instructions
------------

1. Message @botfather https://telegram.me/botfather with the following text: `/newbot`
   If you don't know how to message by username, click the search field on your Telegram app and type `@botfather`, you should be able to initiate a conversation. Be careful not to send it to the wrong contact, because some users has similar usernames to `botfather`.

2. @botfather replies with `Alright, a new bot. How are we going to call it? Please choose a name for your bot.`

3. Type whatever name you want for your bot.

4. @botfather replies with `Good. Now let's choose a username for your bot. It must end in `bot`. Like this, for example: TetrisBot or tetris_bot.`

5. Type whatever username you want for your bot, minimum 5 characters, and must end with `bot`. For example: `whateversamplebot`

6. @botfather replies with:

    Done! Congratulations on your new bot. You will find it at telegram.me/whateversamplebot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands.

    Use this token to access the HTTP API:
    <b>123456789:AAG90e14-0f8-40183D-18491dDE</b>

    For a description of the Bot API, see this page: https://core.telegram.org/bots/api

7. Note down the 'token' mentioned above.

8. Type `/setprivacy` to @botfather.

9. @botfather replies with `Choose a bot to change group messages settings.`

10. Type `@whateversamplebot` (change to the username you set at step 5 above, but start it with `@`)

11. @botfather replies with

    'Enable' - your bot will only receive messages that either start with the '/' symbol or mention the bot by username.
    'Disable' - your bot will receive all messages that people send to groups.
    Current status is: ENABLED

12. Type `Disable` to let your bot receive all messages sent to a group. This step is up to you actually.

13. @botfather replies with `Success! The new status is: DISABLED. /help`

14. Go to https://console.developers.google.com/project

15. Click `Create Project`

16. Type the project name, whatever you want. For example: `octopus-gorilla-123`. Make sure the Project ID is also the same.

17. Clone this repository. If you don't understand what I am saying, click the `Download ZIP` button on the lower-right of this page, and extract the ZIP file.

18. Copy `app.yaml.example` into `app.yaml`. Open the file and change the `YOUR_APP_ID_HERE` to the Project ID you set on step 16, and save the file.

19. Copy `pozo.cfg.example` into `pozo.cfg`. Open the file and change the `YOUR_TELEGRAM_TOKEN` to the token you get from @botfather at step 6. Edit also the `CLIENT_ID` to the imgur API Client-ID ([see here](https://api.imgur.com/)). Finally, set the `ALLOWED_IDS` to a comma-separated list of allowed chat ids.

20. Download Google App Engine SDK for Python from https://cloud.google.com/appengine/downloads and install it.

21. Deploy the application `appcfg.py --oauth2 update /path/to/pozo-bot`

22. Open your browser and go to https://`project-id`.appspot.com/me (replace `project-id` with the Project ID you set on step 16).

23. Wait until you see a long text with `"ok": true` and your bot's name. This could take a minute or so, please reload if it does not succeed.

24. Now, go to https://`project-id`.appspot.com/set_webhook?url=https://`project-id`.appspot.com/webhook (replace both `project-id`s with the Project ID you set on step 16).

25. You should see `Webhook was set`.

26. Open your Telegram client and send the message `/start` to your bot. (type @`your-bot-username` at the search field to initiate the conversation)

27. Try sending more messages and you should see replies from the bot. Mission completed!
