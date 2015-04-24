import os
import sys
import socket
import thread
from time import sleep
import ssl
import collections

def sendQueue(queue, sender):
	"""Hacky send rate limiter"""
	while 1:
		if (len(queue) > 0):
			sender(queue.pop(0))
		sleep(1)

class ircp(object):
	"""A simple IRC client class. Subclass this to implement your own
	IRC applications."""

	def __init__(self):
		"""Open a connection to an IRC server."""
		# self.socket = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.my_nick = None
		self.chans = None
		self.queue = []
		self.tr = thread.start_new_thread(sendQueue, (self.queue, self.send))
		self.handlers = collections.defaultdict(list)

	def __del__(self):
		"""Close the connection."""
		self.quit()

	def hook(self, hook_func, function=None):
		'''Route decorator, @application_instance.hook('say')'''
		def wrapper(function):
			self.handlers[hook_func].append(function)
		return wrapper

	def send(self, string):
		"""Send a string to the server.
		Should only be used by the class, no flood checks."""
		self.socket.send(string + "\n")

	def recv(self):
		"""Read a line from the server. Return None on EOF."""
		line = self.fd.readline()
		if line == "":
			return None
		else:
			s = line.strip()
			return s

	def connect(self, server, port, nick, chans, realname="c45y", password=None):
		"""Log in to the server."""
		self.server = server
		self.socket.connect((self.server, port))
		self.fd = self.socket.makefile("r")

		if password:
			self.send("PASS :" + password)
		self.nick(nick)
		self.send("USER " + nick + " 0 * :" + realname)
		self.chans = chans

	def nick(self, nick):
		self.send("NICK " + nick)
		self.my_nick = nick

	def part(self, chan):
		self.send("PART " + chan)

	def kick(self, channel, nick, reason):
		if reason is None:
			self.send("KICK " + channel + " " + nick)
		else:
			self.send("KICK " + channel + " " + nick + " :" + reason)

	def topic(self, channel, topic):
		self.send("TOPIC " + channel + " :" + topic)

	def quit(self, reason="Quit"):
		"""Quit from the server."""
		self.plugin_send('shutdown', reason)
		try:
			self.send("QUIT :" + reason)
			self.socket.close()
		except:
			pass

	def join(self, channel, key=None):
		"""Join a channel."""
		if key is None:
			self.send("JOIN " + channel)
		else:
			self.send("JOIN " + channel + " " + key)

	def usermode(self, channel, user, mode):
		"""Change a user's modes on a channel."""
		self.send("MODE " + channel + " " + mode + " " + user)

	def op(self, channel, user):
		self.usermode(channel, user, "+o")

	def deop(self, channel, user):
		self.usermode(channel, user, "-o")

	def voice(self, channel, user):
		self.usermode(channel, user, "+v")

	def devoice(self, channel, user):
		self.usermode(channel, user, "-v")

	def say(self, to, text):
		"""Send a message to a user or channel."""
		#self.send("PRIVMSG " + to + " :" + text)
		self.queue.append("PRIVMSG " + to + " :" + text)

	def notice(self, to, text):
		self.send("NOTICE " + to + " :" + text)

	def mainloop(self):
		while 1:
			line = self.recv()
			if not line:
				break
			prefix = None
			if line[0] == ":":
				(prefix, line) = line[1:].split(" ", 1)
			(command, params) = line.split(" ", 1)

			if command[0] >= '0' and command[0] <= '9':
				code = int(command)
				if code == 1:
					for ch in self.chans:
						self.join(ch)
				elif code == 433:
					self.nick(self.my_nick + "_")
				else:
					self.plugin_send('reply', prefix, code, params)
			elif command == "PING":
				self.send("PONG " + params)
			elif command == "NICK":
				l = self.ircsplit(params, 0)
				self.plugin_send('nick', prefix, l[0])
			elif command == "MODE":
				self.plugin_send('mode', prefix, params)
			elif command == "QUIT":
				l = self.ircsplit(params, 0)
				self.plugin_send('quit', prefix, l[0])
			elif command == "JOIN":
				l = self.ircsplit(params, 0)
				self.plugin_send('join', prefix, l[0])
			elif command == "PART":
				l = self.ircsplit(params, 1)
				self.plugin_send('part', prefix, l[0], l[1])
			elif command == "TOPIC":
				l = self.ircsplit(params, 1)
				self.plugin_send('topic', prefix, l[0], l[1])
			elif command == "INVITE":
				l = self.ircsplit(params, 1)
				self.plugin_send('invite', prefix, l[0], l[1])
			elif command == "KICK":
				l = self.ircsplit(params, 2)
				self.plugin_send('kick', prefix, l[0], l[1], l[2])
			elif command == "PRIVMSG":
				l = self.ircsplit(params, 1)
				self.plugin_send('say', prefix, l[0], l[1])
			elif command == "NOTICE":
				l = self.ircsplit(params, 1)
				self.plugin_send('notice', prefix, l[0], l[1])
			else:
				self.plugin_send('command', prefix, command, params)

	def ircsplit(self, s, num):
		"""Split a string of the form word1 word2 .. wordN :string."""
		l = s.split(" ", num)
		if len(l) < (num + 1):
			l.append(None)
		elif l[num][0] == ":":
			l[num] = l[num][1:]
		return l

	def getnick(self, s):
		n = s.find("!")
		if n > -1:
			return s[:n]
		else:
			return s

	def mynick(self):
		return self.my_nick

	def plugin_send(self, method, *args):
		for x in self.handlers[method]:
			x(self, *args)


bot = ircp()
