#!/usr/bin/python
# Copyright 2009 Matt Rudary (matt@rudary.com)

from gameclient.cards import cardlib

import random
import re

from gameclient import util


class Error(Exception):
  """Base exception class for this module."""


class CallException(Error):
  """Errors in creating a Call."""


class Call(object):
  """Base class for calls (e.g. bids, pass, etc)"""
  pass


class Pass(Call):
  pass


class Double(Call):
  pass


class Redouble(Call):
  pass


class Bid(Call):
  class Strain(object):
    def __init__(self, magnitude, suit, abbrevs):
      """Initialize a Strain object.

      Arguments:
        magnitude: An integer used for ordering of Strains.
        suit: A cardlib.Card.Suit, or None for No Trump.
        abbrevs: A list of abbreviations that should map to this strain.
      """
      self.magnitude = magnitude
      if suit is not None and not isinstance(suit, cardlib.Card.Suit):
        raise TypeError('suit should be a cardlib.Card.Suit, not a %s'
                        % type(suit))
      self.suit = suit
      if suit is not None:
        self.name = suit.name
      else:
        self.name = 'No Trump'
      self.abbrevs = abbrevs

    @staticmethod
    def NewStrain(abbrev):
      return Bid.STRAIN_MAP[abbrev]

    def __str__(self):
      return self.name

    def __repr__(self):
      return 'Strain(%d, %s, %s)' % (self.magnitude, repr(self.name),
                                     self.abbrevs)

    # Ordering matters for strains
    def __cmp__(self, other):
      if (isinstance(other, Bid.Strain)):
        if self.magnitude == other.magnitude and self.suit != other.suit:
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

  CLUBS = Strain(0, cardlib.Card.CLUBS, ['C', 'c'])
  DIAMONDS = Strain(1, cardlib.Card.DIAMONDS, ['D', 'd'])
  HEARTS = Strain(2, cardlib.Card.HEARTS, ['H', 'h'])
  SPADES = Strain(3, cardlib.Card.SPADES, ['S', 's'])
  NOTRUMP = Strain(4, None, ['NT', 'nt', 'N', 'n'])

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

  def __str__(self):
    return '%d%s' % (self.level, self.strain.abbrevs[0])

  def __repr__(self):
    return 'Bid(%d, "%s")' % (self.level, self.strain.abbrevs[0])


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


class Contract(object):
  def __init__(self, bid, declarer, doubled=False, redoubled=False):
    """Create a contract.

    Arguments:
      bid: A Bid object indicating the contract level, or None if the
           auction consisted only of passes.
      declarer: A member of rules.players, where rules is the governing
                Rules object.
      doubled: True if the contract has been doubled (but not redoubled.)
      redoubled: True if the contract has been redoubled.
    """
    if bid is not None:
      self.level = bid.level
      self.strain = bid.strain
      self.declarer = declarer
      self.doubled = doubled
      self.redoubled = redoubled
      if self.doubled and self.redoubled:
        raise Error('Contract should not be both doubled and redoubled.')
    else:
      self.level = 0

  def __str__(self):
    if self.level == 0:
      return 'No contract.'
    else:
      if self.doubled:
        d = 'X'
      elif self.redoubled:
        d = 'XX'
      else:
        d = ''
      return '%d%s%s' % (self.level, self.strain.abbrevs[0], d)

  def __repr__(self):
    if self.level == 0:
      return 'Contract(None, None)'
    return ('Contract(Bid(%d, "%s"), %s, %s, %s)'
            % (self.level, self.strain.abbrevs[0], repr(self.declarer),
               str(self.doubled), str(self.redoubled)))


def LastBid(auction):
  """Find the last bid made.

  Arguments:
    auction: A sequence of Call objects.

  Returns:
    A pair containing the index of the last Bid and the Bid itself,
    or (None, None) if there is no Bid in auction.
  """
  bids = [(i, b) for i, b in enumerate(auction) if isinstance(b, Bid)]
  if not len(bids):
    return (None, None)
  return bids[-1]


class RulesException(Error):
  """Base exception class for errors raised by methods of Rules."""


class InsufficientBid(RulesException):
  pass


class IllegalDouble(RulesException):
  """Exception indicating a double or redouble bid is not legal."""


class Rules(object):
  """Run a bridge game. Dreadfully incomplete."""
  def __init__(self, players, dealer=None):
    """Inialize a game of bridge.

    Arguments:
      players: An array of 4 players.
      dealer: An index in [0, 3].

    Raises:
      RulesException: when there's a problem with the arguments.
    """
    cardlib.Card.ACE = cardlib.Card.ACEHI
    self.deck = cardlib.Deck()
    self.players = players
    if len(players) != 4:
      raise RulesException('%d is the wrong number of players.' % len(players))
    if dealer is None:
      self.dealer = self.SelectDealer()
    else:
      self.dealer = dealer
    if self.dealer < 0 or 4 < self.dealer:
      raise RulesException('Illegal initial dealer ' + repr(self.dealer))

  def SelectDealer(self):
    """Returns the index of the dealer."""
    return random.randint(0, 3)

  def _EvaluatePass(self, auction):
    if (3 <= len(auction) and isinstance(auction[-1], Pass)
        and isinstance(auction[-2], Pass)):  # The auction is ended
      idx, last_bid = LastBid(auction)
      if last_bid is None:
        return Contract(None, None)
      partnership = idx % 2
      relevant_bids = [i for i, b in enumerate(auction)
                       if (i % 2 == partnership and isinstance(b, Bid)
                           and b.strain == last_bid.strain)]
      declarer = self.players[(relevant_bids[0] + self.dealer) % 4]
      redoubled = util.ContainsInstance(auction[idx + 1:], Redouble)
      doubled = (not redoubled
                 and util.ContainsInstance(auction[idx + 1:], Double))
      return Contract(last_bid, declarer, doubled, redoubled)
    else:
      return None  # pass is always legal

  def _EvaluateDouble(self, auction):
    idx, last_bid = LastBid(auction)
    if last_bid is None:
      raise IllegalDouble('There must be a bid before you can double.')
    if idx % 2 == len(auction) % 2:
      raise IllegalDouble('You may not double your partner\'s bid.')
    if not reduce(lambda x, y: x and y,
                  map(lambda z: isinstance(z, Pass), auction[idx+1:]),
                  True):
      raise IllegalDouble('There may be no intervening non-Pass calls.')
    return None

  def _EvaluateRedouble(self, auction):
    idx, last_bid = LastBid(auction)
    if last_bid is None:
      raise IllegalDouble('There must be a bid and a double before you'
                          ' may redouble.')
    if (isinstance(auction[-1], Double)
        or (idx < len(auction) - 3 and isinstance(auction[-3], Double)
            and isinstance(auction[-2], Pass)
            and isinstance(auction[-1], Pass))):
      return None
    raise IllegalDouble('You may only redouble your opponent\'s double.')

  def _EvaluateBid(self, auction, candidate):
    idx, last_bid = LastBid(auction)
    if last_bid is None or candidate > last_bid:
      return None
    raise InsufficientBid('%s does not supersede %s.'
                          % (str(candidate), str(last_bid)))

  def EvaluateCall(self, auction, candidate):
    """Determine whether candidate is a legal call, given the auction so far.

    Arguments:
      auction: A sequence of Call objects; assumed to be a legal sequence of
               calls.
      candidate: A Call object.

    Returns:
      None if the candidate is legal but does not end the auction.
      A Contract if the candidate is legal and ends the auction.

    Raises:
      InsufficientBid for insufficient bids.
      IllegalDouble if a double or redouble is not legal.
    """
    if isinstance(candidate, Pass):
      return self._EvaluatePass(auction)
    elif isinstance(candidate, Double):
      return self._EvaluateDouble(auction)
    elif isinstance(candidate, Redouble):
      return self._EvaluateRedouble(auction)
    elif isinstance(candidate, Bid):
      return self._EvaluateBid(auction, candidate)
    raise TypeError('candidate should be a Bid, Double, Redouble, or Pass, '
                    'not a %s.' % type(candidate))

  def EvaluateTrick(self, cards, leader, trump):
    """Determine the winner of a trick.

    Arguments:
      cards: A list of cardlib.Card objects, starting with the card led.
      leader: The offset into self.players of the player on lead.
      trump: The Strain of the contract.

    Returns:
      The offset into self.players of the player who won the trick.
    """
    def winner_from_candidates(s):
      return (max(s, key=lambda x: x[1].rank)[0] + leader) % 4
    if trump is None:
      trumps = []
    else:
      trumps = [(p, c) for p,c in enumerate(cards) if c.suit == trump.suit]
    if trumps:
      return winner_from_candidates(trumps)
    return winner_from_candidates([(p, c) for p,c in enumerate(cards)
                                   if c.suit == cards[0].suit])
