#!/usr/bin/env python
# -*- coding: latin-1 -*-

import struct
import json
import socket
import time
from bot import bot

servers = ['s.nerd.nu', 'p.nerd.nu', 'c.nerd.nu']

@bot.hook('say')
def checkmc(ibot, source, to, message):
	if talking_to_me(message, ibot.my_nick):
		_, args = message.split(' ', 1)
		args = args.split(' ')
	else:
		return

	if args and len(args) >= 1 and args[0] == 'status':
		ibot.say(to, ' '.join(map(try_info, servers)))
	elif args and len(args) >= 1 and args[0] == 'players':
		if len(args) >= 2 and args[1] in servers:
			ibot.say(to, try_players(args[1]))
		else:
			ibot.say(to, "Required server name missing: players <server>" + t())


def talking_to_me(message, me):
	return message.split(' ')[0].rstrip(':, ') == me

def t():
	return " @" + str(int(time.time()))

def try_info(host, port=25565):
	try:
		return "[%s: %s]" % (host, get_info(host)['players']['online'])
	except Exception as e:
		print e
		return "Error contacting " + host + t()

def try_players(host, port=25565):
	try:
		info = get_info(host)
		total = int(info['players']['online'])
		shown = len(info['players']['sample'])
		if total > shown:
			msg = ", and %d more..." % (total - shown)
		else:
			msg = ""
		return "[%s: %s%s]" % (host, ', '.join([x['name'] for x in info['players']['sample']]), msg)
	except Exception as e:
		print e
		return "Error contacting " + host + t()

def get_info(host='localhost', port=25565):
	def unpack_varint(s):
		d = 0
		for i in range(5):
			b = ord(s.recv(1))
			d |= (b & 0x7F) << 7*i
			if not b & 0x80:
				break
		return d

	def pack_varint(d):
		o = ""
		while True:
			b = d & 0x7F
			d >>= 7
			o += struct.pack("B", b | (0x80 if d > 0 else 0))
			if d == 0:
				break
		return o
	
	def pack_data(d):
		return pack_varint(len(d)) + d

	def pack_port(i):
		return struct.pack('>H', i)

	# Connect
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))

	# Send handshake + status request
	s.send(pack_data("\x00\x00" + pack_data(host.encode('utf8')) + pack_port(port) + "\x01"))
	s.send(pack_data("\x00"))

	# Read response
	unpack_varint(s)     # Packet length
	unpack_varint(s)     # Packet ID
	l = unpack_varint(s) # String length

	d = ""
	while len(d) < l:
		d += s.recv(1024)

	# Close our socket
	s.close()

	# Load json and return
	return json.loads(d.decode('utf8'))