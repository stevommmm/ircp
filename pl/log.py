#!/usr/bin/env python
from bot import bot

@bot.hook('nick')
def nick(bot, old, new):
    print 'NICK', old, new

@bot.hook('mode')
def mode(bot, nick, modes):
    print 'MODE', nick, modes

@bot.hook('quit')
def quit(bot, nick, reason):
    print 'QUIT', nick, reason

@bot.hook('join')
def join(bot, nick, channel):
    print 'JOIN', nick, channel

@bot.hook('part')
def part(bot, nick, channel, reason):
    print 'PART', nick, channel, reason

@bot.hook('topic')
def topic(bot, nick, channel, topic):
    print 'TOPIC', nick, channel, topic

@bot.hook('invite')
def invite(bot, source, to, channel):
    print 'INVITE', source, to, channel

@bot.hook('kick')
def kick(bot, source, channel, to, reason):
    print 'KICK', source, channel, to, reason

@bot.hook('say')
def say(bot, source, to, message):
    print 'SAY', source, to, message

@bot.hook('notice')
def notice(bot, source, to, message):
    print 'NOTICE', source, to, message

@bot.hook('unknown')
def unknown(bot, prefix, command, params):
    print 'UNKNOWN', prefix, command, params

@bot.hook('reply')
def reply(bot, prefix, code, params):
    print 'REPLY', prefix, code, params

@bot.hook('command')
def command(bot, prefix, command, params):
    print 'COMMAND', prefix, command, params