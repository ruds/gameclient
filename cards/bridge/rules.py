#!/usr/bin/python
# Copyright 2009 Matt Rudary (matt@rudary.com)

import random
import re

from cards import cardlib


class Error(Exception):
  """Base exception class for this module."""


class CallException(Error):
  """Errors in creating a Call."""


class Call(object):
  pass


class Pass(Call):
  pass


class Double(Call):
  pass


class Redouble(Call):
  pass


class Bid(Call):
  class Strain(object):
    def __init__(self, magnitude, name, abbrevs):
      self.magnitude = magnitude
      self.name = name
      self.abbrevs = abbrevs

    def __str__(self):
      return self.name

    def __repr__(self):
      return 'Strain(%d, %s, %s)' % (self.magnitude, self.name, self.abbrevs)

    def __cmp__(self, other):
      if (isinstance(other, Bid.Strain)):
        if (self.magnitude == other.magnitude
            and (self.name != other.name
                 or self.abbrevs != other.abbrevs)):
          raise Error('These are weird strains: %s, %s' % (repr(self),
                                                           repr(other)))
        return cmp(self.magnitude, other.magnitude)
      elif (isinstance(other, str)):
        try:
          return cmp(self, Bid.STRAIN_MAP[other])
        except KeyError:
          raise TypeError('When comparing a Strain to a str, the str should'
                          ' be in Bid.STRAIN_MAP. "%s" is not.' % other)
      raise TypeError('Expected Strain or str when comparing to a Strain.'
                      ' other is of type %s.' % str(type(other)))

  CLUBS = Strain(0, 'Clubs', ['C', 'c'])
  DIAMONDS = Strain(1, 'Diamonds', ['D', 'd'])
  HEARTS = Strain(2, 'Hearts', ['H', 'h'])
  SPADES = Strain(3, 'Spades', ['S', 's'])
  NOTRUMP = Strain(4, 'No Trump', ['NT', 'nt', 'N', 'n'])

  STRAINS = [CLUBS, DIAMONDS, HEARTS, SPADES, NOTRUMP]
  STRAIN_MAP = dict([(a, s) for s in STRAINS for a in s.abbrevs]
                    + [(s.name, s) for s in STRAINS])

  def __init__(self, level, strain):
    """Initialize the bid.

    Arguments:
      level: An integer between 1 and 7.
      strain: A member of Bid.STRAINS or a key in Bid.STRAIN_MAP
    """
    if not isinstance(level, int) or level < 1 or 7 < level:
      raise CallException(repr(level) + ' is an invalid level')
    self.level = level
    if isinstance(strain, Bid.Strain):
      self.strain = strain
    elif strain in Bid.STRAIN_MAP:
      self.strain = Bid.STRAIN_MAP[strain]
    else:
      raise CallException('%s is an invalid strain' % repr(strain))

  def __cmp__(self, other):
    if not isinstance(other, Bid):
      raise TypeError('Cannot compare a Bid to a %s' % str(type(other)))
    if self.level == other.level:
      return cmp(self.strain, other.strain)
    else:
      return cmp(self.level, other.level)


def NewCall(S):
  """Build a Call from S.

  Arguments:
    S: A string that encodes the call. e.g. '1H', '2c', 'X', '-'. It
       should be one or two characters long, with:
         pass represented by one of 'p', 'P', '-', or any
           capitalization of 'pass';
         double represented by 'x' or 'X';
         redouble represented by 'xx' or 'XX';
         bids represented by a numeral and one of 's', 'S', 'h', 'H',
           'd', 'D', 'c', 'C', 'n', 'N', 'nt', or 'NT'.

  Returns:
    A Call object.
  """
  s = S.lower()
  if s in ['pass', 'p', '-']:
    return Pass()
  if s == 'x':
    return Double()
  if s == 'xx':
    return Redouble()

  m = re.match('([1-7])([nshdc]|nt)$', s)
  if m is not None:
    return Bid(int(m.group(1)), m.group(2))
  raise CallException('"%s" did not compute as a call.' % S)


class Rules(object):
  """Run a bridge game. Dreadfully incomplete."""

  def __init__(self, players, initial_player=None):
    self.deck = cardlib.Deck()
    self.players = players
    assert len(players) == 4
    if initial_player is None:
      self.current_player = self.SelectFirstPlayer()

  def SelectFirstPlayer(self):
    return random.randint(0, 3)
