#!/usr/bin/python
# Copyright 2009 Matt Rudary (matt@rudary.com)

from gameclient.cards import cardlib

import unittest


class TestDeck(unittest.TestCase):
  def setUp(self):
    self.deck = cardlib.Deck()

  def testPick(self):
    card = self.deck.Pick()
    self.assert_(isinstance(card, cardlib.Card))
    card_list = self.deck.Pick(1)
    self.assertEqual(len(card_list), 1)
    self.assertEqual(len(self.deck.Pick(50)), 50)
    self.assertRaises(cardlib.EmptyDeckException, self.deck.Pick, 1)

  def testDeck(self):
    self.deck.Shuffle(lambda x, r=None: list.sort(x, key=lambda c: c.value()))
    self.assertEqual(''.join(map(lambda x: ('%c%c' %
                                            (cardlib.Card.RankShort(x.rank()),
                                             cardlib.Card.SuitShort(x.suit()))),
                                 self.deck.Pick(52))),
                     "2C3C4C5C6C7C8C9C0CJCQCKCAC" +
                     "2D3D4D5D6D7D8D9D0DJDQDKDAD" +
                     "2H3H4H5H6H7H8H9H0HJHQHKHAH" +
                     "2S3S4S5S6S7S8S9S0SJSQSKSAS")

if __name__ == '__main__':
  unittest.main()
