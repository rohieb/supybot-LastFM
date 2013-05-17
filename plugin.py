###
# Copyright (c) 2009, Roland Hieber
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import csv
import supybot.utils as utils
import supybot.conf as conf
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import urllib

class Lastfm(callbacks.Plugin):
  """Provides the lastfm command which shows the last played track """
  """of a LastFM user"""
  pass

  def __init__(self, irc):
    self.__parent = super(Lastfm, self)
    self.__parent.__init__(irc)
    self.filename = conf.supybot.directories.data.dirize('Lastfm.db')
    self.nicklist = dict()
    self._loadNicks()

  # load alternate nicks
  def _loadNicks(self):
    try:
      fd = file(self.filename)
    except EnvironmentError, e:
      self.log.warning('Couldn\'t open %s: %s', self.filename, e)
      return
    reader = csv.reader(fd)
    for (nick, username) in reader:
      self.nicklist[nick] = username
    fd.close()

  # save nicks
  def _flushNicks(self):
    fd = utils.file.AtomicFile(self.filename)
    writer = csv.writer(fd)
    for nick, username in self.nicklist.iteritems():
      writer.writerow([nick, username])
    fd.close()

  # set default username for nick
  def setUser(self, irc, msg, args, user):
    """[<username>]

    Sets the Last.FM username to use as default for your requests. If username
    is not given, the default value for your nick is deleted."""

    if user == None or user == "":
      if msg.nick in self.nicklist.keys():
        del(self.nicklist[msg.nick])
      irc.reply("Your default LastFM username has been deleted.")
    else:
      self.nicklist[msg.nick] = user
      irc.replySuccess()
    self._flushNicks()

  setuser = wrap(setUser, [additional('anything', None)])

  # get default username for nick
  def getUser(self, irc, msg, args):
    """Displays the Last.FM username to use as default for your requests."""

    if msg.nick not in self.nicklist.keys():
      irc.reply("No username has been set as default.")
    else:
      irc.reply("Your LastFM username defaults to "+self.nicklist[msg.nick]);

  getuser = wrap(getUser, [])

  # query current track
  def lastfm(self, irc, msg, args, user):
    """[<user>]

    Shows the last played track of a LastFM user specified by <user>. If 
    <user> is empty, your default username (set with setuser) or if 
    emtpy, your IRC nickname is used as the Last.FM username."""

    if user == "":
      if msg.nick in self.nicklist.keys():
        user = self.nicklist[msg.nick]
      else:
        user = msg.nick

    f = urllib.urlopen("http://phenny-ws.appspot.com/lastfm/" + user)
    s = f.read()
    irc.reply(str(s.strip()), prefixNick = True)
    f.close()

  lastfm = wrap(lastfm, [additional(('anything'), "")])

Class = Lastfm


# vim:set shiftwidth=2 tabstop=2 expandtab textwidth=79:
