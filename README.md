IRCp
----

A modular irc bot for basic botting needs.

Plugins are contained in the `/pl/` folder, and are handled by hooks in the following format

    @bot.hook('join')
    def join(bot, nick, channel):
        print 'JOIN', nick, channel
        
Running without `-d` will run the bot in the foreground.