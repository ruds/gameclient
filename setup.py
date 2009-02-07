#!/usr/bin/env python

from distutils.core import setup

setup(name='gameclient',
      version='0.1',
      description='Distributed Game-playing Software',
      author='Matt Rudary',
      author_email='matt@rudary.com',
      url='http://gameclient.googlecode.com/',
      packages=['gameclient',
                  'gameclient.cards',
                    'gameclient.cards.bridge',
                ],
      data_files=[('gameclient/scripts', ['run_tests.py'])],
      )
