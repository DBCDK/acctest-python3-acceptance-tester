#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""
:mod:`acceptance_tester.framework.aux` -- Auxillary functions
=============================================================

===================
Auxillary Functions
===================

Contains auxillary functions used across modules
"""
import logging


class NullHandler( logging.Handler ):
    """
    Nullhandler for logging.
    """

    def emit( self, record ):
        pass

### define logger
logger = logging.getLogger( "dbc."+__name__ )
logger.addHandler( NullHandler() )


def delta_str( delta ):
    """
    Builds and returns a formatted string representing delta.

    :param delta:
        The delta to format and return
    :type delta:
        datetime.delta
    :return:
        Formatted string representation of delta
    """
    seconds = delta.seconds
    logger.debug( "Seconds: %s", seconds )
    zlpad = lambda num, length: "0"*( length-len( str( num ) ) ) + str( num )

    tstr = "%s seconds"%seconds

    minutes = int(seconds / 60)
    if minutes > 0:
        seconds = seconds % 60
        tstr = "%s:%s minutes"%( minutes, zlpad( seconds, 2 ) )
    hours = int(minutes / 60)
    if hours > 0:
        minutes = minutes % 60
        tstr = "%s:%s:%s hours"%( hours, zlpad( minutes, 2 ), zlpad( seconds, 2 ) )
    logger.debug( "Formatted value '%s' ==> '%s'", delta, tstr )
    return tstr


def datetime_str( time ):
    """ Creates pretty string rep of datetime
    """
    return "%04d-%02d-%02d %02d:%02d:%02d"%( int(time.year), int(time.month), int(time.day), int(time.hour), int(time.minute), int(time.second) )


def format_description( string, length = 80, prefix = 'Description: ' ):
    """
    Formats description string
    """
    try:
        strlen = length - len( prefix )

        result = []
        string = " ".join( [x.strip() for x in [x for x in string.split( "\n" ) if x != '']] )

        first_time = True
        while( string != '' ):
            index = strlen
            if strlen >= len( string ):
                substr = string
                string = ''
            else:
                while( string[index] != ' '):
                    index -= 1
                substr = string[:index]
                string = string[index:].strip()

            if first_time:
                substr = prefix + substr
                first_time = False
            else:
                substr = ( " " * len( prefix ) ) + substr
            result.append( substr )

        return "\n".join( result )

    except:
        logger.warning( "Could not format description '%s'"%string )
        return string
