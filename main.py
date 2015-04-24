#!/bin/env python

import os
import sys

# Import plugins
from bot import bot
from pl import *


def daemonize():
	try: 
		pid = os.fork() 
		if pid > 0:
			# exit first parent
			sys.exit(0) 
	except OSError, e: 
		sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
		sys.exit(1)

	# decouple from parent environment
	os.chdir(".") 
	os.setsid() 
	os.umask(0) 

	# do second fork
	try: 
		pid = os.fork() 
		if pid > 0:
			# exit from second parent
			sys.exit(0) 
	except OSError, e: 
		sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
		sys.exit(1) 
	
	# redirect standard file descriptors
	si = open(os.devnull, 'r')
	so = open('botout.log', 'a+')
	se = open('boterr.log', 'a+', 0)
	
	pid = str(os.getpid())
	
	sys.stderr.write("\n%s\n" % pid)
	sys.stderr.flush()

	open('bot.pid','w+').write("%s\n" % pid)
	
	os.dup2(si.fileno(), sys.stdin.fileno())
	os.dup2(so.fileno(), sys.stdout.fileno())
	os.dup2(se.fileno(), sys.stderr.fileno())


if __name__ == '__main__':
	if not '-d' in sys.argv:
		daemonize()

	try:
		bot.connect('irc.gamesurge.net', 6667, 'eri', ['#redditmc', '#llama'])
		bot.mainloop()
	except KeyboardInterrupt:
		bot.quit('Got Ctrl + C')
	except Exception as e:
		print e
		bot.quit(repr(e))
