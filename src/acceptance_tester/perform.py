#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""
:mod:`acceptance_tester.perform` -- parses file for performace lines
====================================================================

=======
Perform
=======

Parses file and picks up lines that conforms to a particular
format. The lines are parsed, and the found values are handled and
written to property files, that can be used by the `Jenkins Plot
Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Plot+Plugin>`_.

performance format::

   [PERFORMANCE:($name, $method, $time)]

lines that contain this pattern is picked up by the parser.

1. The $name variable is the name of the performance class that is
   contained in this line. The $name is used in the properties
   filename like ($name).properties.

2. The $method variable is how this particular performance class is
   evaluated. Supported methods are *sum* and *avg*. If multiple types
   are provided in succesive lines the first provided method is used.

3. The $time variable provides the actual measurement. This should
   conform to the pattern used by :class:`timedate.delta`.

A performance logline could be created in python like this::

   start = datetime.datetime.now()
   # Functionality to time
   delta = start - datetime.datetime.now()
   logger.debug( '[PERFORMANCE:(name, sum, %s)]'%delta )


Commandline options
-------------------

.. cmdoption:: -o <output-folder> --output-folder <output-folder>

      Folder to place property files in. The folder is created if it
      doesn't exist.
"""
import datetime
import os
import re


def parse_stamp( stamp ):
    """ Parses timestamp string and creates a timedelta object """
    stamp = stamp.strip( '\'' )

    ( h, m, s ) = stamp.split( ":" )
    ( s, ms ) = s.split( "." )
    delta = datetime.timedelta( hours = int( h ),
                                minutes = int( m ),
                                seconds = int( s ),
                                microseconds= int( ms ) )
    return delta


def parse_file( file ):
    """ Creates dict with performance values found in file """
    values = dict()
    regex = ".*?\[PERFORMANCE: *\( *(.*?) *, *((?:avg)|(?:sum)) *, *(.*?)\)\].*"

    fh = open( file )
    for line in fh.readlines():

        match = re.match( regex, line )
        if match:

            if not match.group( 1 ) in values:
                values[match.group( 1 )] = dict()
                values[match.group( 1 )]['values'] = []
                values[match.group( 1 )]['method'] = match.group( 2 )

            values[ match.group( 1 ) ]['values'].append( parse_stamp( match.group( 3 ) ) )

    fh.close()
    return values


def create_folder( outputfolder ):
    """ Creates folder if it doesn't exist """
    outputfolder = os.path.abspath( outputfolder )
    if not os.path.exists( outputfolder ):
        os.mkdir( outputfolder )
    return outputfolder


def write_output_files( values, outputfolder ):
    """ write property files for each entry in the values dict """
    outputfolder = create_folder( outputfolder )
    for key, value in values.iteritems():

        yvalue = reduce( lambda x, y: x + y, value['values'] ) # sum of the values
        if value['method'] == 'avg':
            yvalue = yvalue / len( value['values'] )

        fh = open( os.path.join( outputfolder, "%s.properties"%key ), 'w' )
        fh.write( 'YVALUE=%s\n'%yvalue.seconds )
        fh.close()


def perform( file, outputfolder ):
    """ parses file and write corresponding property files in outputfolder"""
    values = parse_file( file )
    write_output_files( values, outputfolder )


if __name__ == '__main__':

    from optparse import OptionParser
    import sys

    parser = OptionParser( usage="%prog [options] file\n Creates properties files containing timimgs," +
                           "from date found in file. The property files can be picked up by the" +
                           "jenkins plot plugin" )

    default_ofolder = os.path.join( os.getcwd(), "timings" )
    parser.add_option("-o", "--output-folder", type="string", action="store", dest="output_folder",
                      default=default_ofolder,
                      help="Folder to place generated properties in. Default is %s"%default_ofolder )

    ( options, args ) = parser.parse_args()

    if len( args ) < 1:
        print "Need file to parse!"
        sys.exit( 1 )

    if not os.path.exists( args[0] ):
        print "file '%s' doesn't exist!"%args[0]
        sys.exit( 1 )

    perform( args[0], options.output_folder )
