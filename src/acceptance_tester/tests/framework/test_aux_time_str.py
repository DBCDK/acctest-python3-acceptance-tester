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

    def test_seconds_used_as_unit_if_delta_is_less_than_a_minute( self ):
        """
        Tests that the resulting string uses seconds as unit
        """
        start = datetime.datetime( 2010, 12, 24, 10, 10, 10 )
        end = datetime.datetime( 2010, 12, 24, 10, 11, 9 )
        result = delta_str( end - start )
        self.assertEqual( "59 seconds", result )

    def test_minutes_used_as_unit_if_delta_is_less_than_a_hour( self ):
        """
        Tests that the resulting string uses minutes as unit
        """
        start = datetime.datetime( 2010, 12, 24, 10, 10, 10 )
        end = datetime.datetime( 2010, 12, 24, 10, 11, 11 )
        result = delta_str( end - start )
        self.assertEqual( "1:01 minutes", result )

    def test_hours_used_as_unit_if_delta_is_more_than_a_hour( self ):
        """
        Tests that the resulting string uses hours as unit
        """

        start = datetime.datetime( 2010, 12, 24, 10, 10, 10 )
        end = datetime.datetime( 2010, 12, 24, 11, 11, 9 )
        result = delta_str( end - start )
        self.assertEqual( "1:00:59 hours", result )

if __name__ == '__main__':
    unittest.main()
