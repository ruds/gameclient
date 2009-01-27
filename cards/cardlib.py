#!/usr/bin/python
# Copyright 2009 Matt Rudary (matt@rudary.com)

import random


class Error(Exception):
  """Base exception class for this module."""


class EmptyDeckException(Error):
  """Your deck is out of cards."""


class Card(object):
  """Represents a playing card."""
  SPADES = 3
  HEARTS = 2
  DIAMONDS = 1
  CLUBS = 0

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
    self._suit = suit
    self._rank = rank

  def suit(self):
    return self._suit
  def rank(self):
    return self._rank

  def value(self):
    return (self._suit, self._rank)

  @staticmethod
  def Suits():
    return xrange(4)

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
    return {Card.SPADES: 'S', Card.HEARTS: 'H', Card.DIAMONDS: 'D',
            Card.CLUBS: 'C'}[suit]


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
