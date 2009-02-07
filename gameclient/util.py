#!/usr/bin/python
# Copyright 2009 Matt Rudary (matt@rudary.com)

def ContainsInstance(s, cls):
  """Determines whether s contains an instance of class cls.

  Arguments:
    s: An iterable object.
    cls: An object of type class.

  Returns:
    True if s contains an instance of cls, False otherwise.
  """
  return reduce(lambda x, y: x or y,
                map(lambda x: isinstance(x, cls), s), False)
