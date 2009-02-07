#!/usr/bin/python
# Copyright 2009 Matt Rudary (matt@rudary.com)

import gameclient.util

import unittest


class TestUtil(unittest.TestCase):
  def testContainsInstance(self):
    self.failUnless(util.ContainsInstance([1, 2, 3, 4], int))
    self.failUnless(util.ContainsInstance([1.0, 2.0, 3, 4.0], int))
    self.failIf(util.ContainsInstance([1.1, 2.0, 3.14159, 4.0], int))
    self.failIf(util.ContainsInstance([], int))

    def generate_ints():
      for i in [1, 2, 3, 4]: yield i

    self.failUnless(util.ContainsInstance(generate_ints(), int))
    self.failIf(util.ContainsInstance(generate_ints(), str))

if __name__ == '__main__':
  unittest.main()
