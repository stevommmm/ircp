#!/bin/python

# Import plugins
from bot import bot
from pl import *


if __name__ == '__main__':
	try:
		bot.connect('irc.gamesurge.net', 6667, 'eri', ['#redditmc', '#llama'])
		bot.mainloop()
	except KeyboardInterrupt:
		bot.quit('Got Ctrl + C')
	except Exception as e:
		print e
		bot.quit(repr(e))
