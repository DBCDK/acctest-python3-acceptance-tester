#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
import os
from optparse import OptionParser
import datetime

import framework.find_tests as find_tests
import framework.rst_creator as rst_creator


def create_report( test_folder, output_folder, start, delta ):

    test_type, test_type_name, tests = find_tests.find_valid_tests( [test_folder], None )
    data = []

    for test in tests:

        entry = { 'xml': test[2],
                  'type-name': test_type_name,
                  'build-folder': test[0],
                  'test-suite': test[0] }

        data.append( entry )

    rst_creator.create_test_documentation( data, output_folder, start, delta )


def parse_datetimestr( string ):

    print "Parsing date '%s'"%string

    spl = string.split( " " )
    year, month, day = spl[0].split( "-" )

    hour, minute, second = spl[1].split( ":" )

    if "." in second:
        second, microsecond = second.split( "." )
    else:
        microsecond = "00"

    vals = map( int, [year, month, day, hour, minute, second, microsecond] )
    return datetime.datetime( *vals )


def cli():

    usage="Builds test-report."

    parser = OptionParser( usage="%prog -s starttime -e endtime testfolder outputfolder\n" + usage )

    parser.add_option( "-s", "--start-time", type="string", action="store", dest="start_time",
                       help="""The start time of the test. example time: '2012-10-08 21:42:01.696181'.
                               This is the format you get if you print a python datetime.datetime object""",
                       default=None )

    parser.add_option( "-e", "--end-time", type="string", action="store", dest="end_time",
                       help="""The end time of the test. example time: '2012-10-08 21:42:01.696181'.
                               This is the format you get if you print a python datetime.datetime object""",
                       default=None )

    ( options, args ) = parser.parse_args()

    if len(args) < 2:
        parser.error( "Needs testfolder and outputfolder arguments." )


    if options.start_time == None:
        parser.error( "Needs start-time argument" )

    if options.end_time == None:
        parser.error( "Needs end-time argument" )

    start_time = parse_datetimestr( options.start_time )
    end_time = parse_datetimestr( options.end_time )

    create_report( os.path.abspath( args[0] ), os.path.abspath( args[1] ), start_time, end_time-start_time )

