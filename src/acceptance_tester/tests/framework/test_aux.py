#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-

import datetime
import os.path
import sys
import unittest


sys.path.insert( 0, os.path.dirname( os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( sys.argv[0] ) ) ) ) ) )
from acceptance_tester.framework.aux import delta_str


class Test_delta_str( unittest.TestCase ):

    def test_delta_str_is_less_than_a_minute( self ):
        """
        Tests that the resulting string uses seconds as unit
        """
        result = delta_str( datetime.timedelta(seconds=59) )
        self.assertEqual( "59 seconds", result )

    def test_delta_str_is_less_than_a_hour( self ):
        """
        Tests that the resulting string uses minutes as unit
        """
        result = delta_str( datetime.timedelta(seconds=61) )
        self.assertEqual( "1:01 minutes", result )

    def test_delta_str_is_more_than_a_hour( self ):
        """
        Tests that the resulting string uses hours as unit
        """

        result = delta_str( datetime.timedelta( hours=1, seconds= 59 ) )
        self.assertEqual( "1:00:59 hours", result )

if __name__ == '__main__':
    unittest.main()
