#!/usr/bin/python
# Copyright 2009 Matt Rudary (matt@rudary.com)

from gameclient.cards.bridge import rules

import unittest

class TestCall(unittest.TestCase):
  def setUp(self):
    pass

  def testStrainOrdering(self):
    self.assertEqual(map(lambda x: x.name, sorted(rules.Bid.STRAINS)),
                     ['Clubs', 'Diamonds', 'Hearts', 'Spades', 'No Trump'])
    self.assertEqual(sorted(rules.Bid.STRAINS), rules.Bid.STRAINS)
    self.failUnless(rules.Bid.CLUBS < 'H')

  def testNewCall(self):
    self.failUnless(isinstance(rules.NewCall('pass'), rules.Pass))
    self.failUnless(isinstance(rules.NewCall('PASS'), rules.Pass))
    self.failUnless(isinstance(rules.NewCall('-'), rules.Pass))
    self.failUnless(isinstance(rules.NewCall('X'), rules.Double))
    self.failUnless(isinstance(rules.NewCall('XX'), rules.Redouble))
    self.failUnless(isinstance(rules.NewCall('7H'), rules.Bid))
    self.failUnless(isinstance(rules.NewCall('4c'), rules.Bid))
    self.failUnless(isinstance(rules.NewCall('1NT'), rules.Bid))
    self.assertRaises(rules.Error, rules.NewCall, '8NT')
    self.assertRaises(rules.Error, rules.NewCall, '0NT')
    self.assertRaises(rules.Error, rules.NewCall, 'XX2')
    self.assertRaises(rules.Error, rules.NewCall, '2X')
    self.assertRaises(rules.Error, rules.NewCall, '3f')

  def testBidOrdering(self):
    self.failUnless(rules.Bid(7, 'H') > rules.Bid(6, 'H'))
    self.failUnless(rules.Bid(2, 'S') < rules.Bid(2, 'NT'))
    self.failUnless(rules.Bid(2, 'S') > rules.Bid(1, 'NT'))
    self.assertEqual(rules.Bid(2, 'C'), rules.Bid(2, 'C'))
    self.failUnless(rules.Bid(3, 'C') < rules.Bid(3, 'D'))


class TestRules(unittest.TestCase):
  def setUp(self):
    self.players = ['N', 'E', 'S', 'W']
    self.rules = rules.Rules(players=self.players, dealer=0)

  def _MakeAuction(self, calls):
    auction = []
    for call in map(rules.NewCall, calls):
      self.failUnless(self.rules.EvaluateCall(auction, call) is None)
      auction.append(call)
    return auction

  def testEvaluateCall(self):
    self.assertRaises(TypeError, self.rules.EvaluateCall, [], rules.Call())

    auction1 = self._MakeAuction(['-', '-', '-'])
    # - - - 1H
    self.failUnless(self.rules.EvaluateCall(auction1, rules.NewCall('1H'))
                    is None)
    # - - - -
    con = self.rules.EvaluateCall(auction1, rules.NewCall('-'))
    self.failUnless(isinstance(con, rules.Contract))
    self.assertEqual(con.level, 0)
    # - - - X
    self.assertRaises(rules.IllegalDouble,
                      self.rules.EvaluateCall, auction1, rules.NewCall('X'))
    # - - - XX
    self.assertRaises(rules.IllegalDouble,
                      self.rules.EvaluateCall, auction1, rules.NewCall('XX'))

    auction2 = self._MakeAuction(['1H', '-', '-'])
    # 1H - - 1H
    self.assertRaises(rules.InsufficientBid,
                      self.rules.EvaluateCall, auction2, rules.NewCall('1H'))
    # 1H - - 1C
    self.assertRaises(rules.InsufficientBid,
                      self.rules.EvaluateCall, auction2, rules.NewCall('1C'))
    # 1H - - 1S
    self.failUnless(self.rules.EvaluateCall(auction2, rules.NewCall('1S'))
                    is None)
    # 1H - - -
    con = self.rules.EvaluateCall(auction2, rules.NewCall('-'))
    self.failUnless(isinstance(con, rules.Contract))
    self.assertEqual(con.level, 1)
    self.assertEqual(con.strain, 'H')
    self.assertEqual(con.declarer, self.players[0])
    self.assertEqual(con.doubled, False)
    self.assertEqual(con.redoubled, False)
    # 1H - - X
    self.failUnless(self.rules.EvaluateCall(auction2, rules.NewCall('X'))
                    is None)
    # 1H - - XX
    self.assertRaises(rules.IllegalDouble,
                      self.rules.EvaluateCall, auction2, rules.NewCall('XX'))

    auction3 = self._MakeAuction(['1H', 'X', '-'])
    # 1H X - 1H
    self.assertRaises(rules.InsufficientBid,
                      self.rules.EvaluateCall, auction3, rules.NewCall('1H'))
    # 1H X - 1C
    self.assertRaises(rules.InsufficientBid,
                      self.rules.EvaluateCall, auction3, rules.NewCall('1C'))
    # 1H X - 1S
    self.failUnless(self.rules.EvaluateCall(auction3, rules.NewCall('1S'))
                    is None)
    # 1H X - -
    self.failUnless(self.rules.EvaluateCall(auction3, rules.NewCall('-'))
                    is None)
    # 1H X - X
    self.assertRaises(rules.IllegalDouble,
                      self.rules.EvaluateCall, auction3, rules.NewCall('X'))
    # 1H X - -
    # XX
    self.failUnless(self.rules.EvaluateCall(auction3 + [rules.NewCall('-')],
                                            rules.NewCall('XX'))
                    is None)


    # -  1H X  1S
    # -  2S -  -
    # -
    con = self.rules.EvaluateCall(self._MakeAuction(['-', '1H', 'X', '1S',
                                                     '-', '2S', '-', '-']),
                                  rules.NewCall('-'))
    self.failUnless(isinstance(con, rules.Contract))
    self.assertEqual(con.level, 2)
    self.assertEqual(con.strain, 'S')
    self.assertEqual(con.declarer, self.players[3])
    self.assertEqual(con.doubled, False)
    self.assertEqual(con.redoubled, False)

    # -  1H -  1S
    # -  2N X  -
    # -  3C -  3N
    # X  -  -  XX
    # -  -  -
    auction4 = self._MakeAuction(['-', '1H', '-', '1S',
                                  '-', '2N', 'X', '-',
                                  '-', '3C', '-', '3N',
                                  'X', '-',  '-', 'XX',
                                  '-', '-'])
    con = self.rules.EvaluateCall(auction4, rules.NewCall('-'))
    self.failUnless(isinstance(con, rules.Contract))
    self.assertEqual(con.level, 3)
    self.assertEqual(con.strain, 'N')
    self.assertEqual(con.declarer, self.players[1])
    self.assertEqual(con.doubled, False)
    self.assertEqual(con.redoubled, True)
    # replace 3rd pass w/ X
    self.assertRaises(rules.IllegalDouble,
                      self.rules.EvaluateCall, auction4, rules.NewCall('X'))

if __name__ == '__main__':
  unittest.main()
