#!/usr/bin/python
# Copyright 2009 Matt Rudary (matt@rudary.com)

import random


class Error(Exception):
  """Base exception class for this module."""


class EmptyDeckException(Error):
  """Your deck is out of cards."""


class Card(object):
  """Represents a playing card."""
  class Suit(object):
    def __init__(self, name, abbrev):
      self.name = name
      self.abbrev = abbrev

    def __cmp__(self, other):
      """Somewhat arbitrary, but oh well."""
      return cmp(self.name, other.name)

    def __str__(self):
      return self.name
    def __repr__(self):
      return 'Suit(%s, %s)' % (self.name, self.abbrev)

  CLUBS = Suit('Clubs', 'C')
  DIAMONDS = Suit('Diamonds', 'D')
  HEARTS = Suit('Hearts', 'H')
  SPADES = Suit('Spades', 'S')

  ACEHI = 14
  KING = 13
  QUEEN = 12
  JACK = 11
  TEN = 10
  NINE = 9
  EIGHT = 8
  SEVEN = 7
  SIX = 6
  FIVE = 5
  FOUR = 4
  THREE = 3
  TWO = 2
  ACELO = 1
  # rules engines should set ACE to ACEHI or ACELO to reflect the 
  # default ordering of the cards if one exists
  ACE = ACEHI

  def __init__(self, suit, rank):
    """Initialize a Card.

    Arguments:
      suit: A Card.Suit object.
      rank: One of Card.ACE, Card.TWO, ...
    """
    self.suit = suit
    self.rank = rank

  def value(self):
    return (self.suit, self.rank)

  @staticmethod
  def Suits():
    return [Card.CLUBS, Card.DIAMONDS, Card.HEARTS, Card.SPADES]

  @staticmethod
  def Ranks():
    if Card.ACE == Card.ACELO:
      return xrange(1, 14)
    elif Card.ACE == Card.ACEHI:
      return xrange(2, 15)
    else:
      return range(2,14) + [Card.ACE]

  @staticmethod
  def RankShort(rank):
    if 1 < rank and rank < 10:
      return '%d' % rank
    return {Card.TEN: '0', Card.JACK: 'J', Card.QUEEN: 'Q', Card.KING: 'K',
            Card.ACE: 'A', Card.ACEHI: 'A', Card.ACELO: 'A'}[rank]

  @staticmethod
  def SuitShort(suit):
    return suit.abbrev


class Deck(object):
  """Represents a deck of playing cards."""
  def __init__(self):
    self._deck = []
    for suit in Card.Suits():
      for rank in Card.Ranks():
        self._deck.append(Card(suit, rank))
    self.Shuffle()

  def Shuffle(self, shuf=random.shuffle):
    """Shuffle the cards remaining in the deck.

    Arguments:
      shuf: A function shuf(x[, r]) that shuffles a sequence x in
            place and, optionally, a function r() that returns floats in
            [0.0, 1.0).
    """
    shuf(self._deck)

  def Pick(self, n=None):
    """Take cards off the top of the deck.

    Note: The back of the list is treated as the top of the deck.

    Arguments:
      n: An integer; the number of cards to take.

    Returns:
      By default, a single Card. If n is not None, a sequence
      containing n Cards.
    """
    if n is None:
      if len(self._deck) == 0:
        raise EmptyDeckException("No more cards.")
      return self._deck.pop()

    if n > 0:
      if len(self._deck) < n:
        raise EmptyDeckException("Tried to take %d cards; %d remaining." %
                                 (n, len(self._deck)))
      cards = self._deck[-n:]
      del self._deck[-n:]
      return cards
    return []
