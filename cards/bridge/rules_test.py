#!/usr/bin/python
# Copyright 2009 Matt Rudary (matt@rudary.com)

from cards.bridge import rules

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
    self.rules = rules.Rules()

if __name__ == '__main__':
  unittest.main()
