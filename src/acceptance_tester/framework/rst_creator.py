#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""
:mod:`acceptance_tester.framework.rst_creator` -- Creates rst documentation of testrun
======================================================================================

===========
Rst Creator
===========

The main function in this module is :func:`create_test_documentation`,
which creates rst/sphinx documentation from test results.

A Rst file is created for each test consisting of commentary fields
and raw xml.  Furthermore a index tree is created and written. The
index uses the sphinxs directive 'doc', and the created files are
designed to be part of a sphinx document structure.
"""
import logging
import io
import os.path
from lxml import etree

from acceptance_tester.framework.aux import delta_str


class NullHandler( logging.Handler ):
    """
    Nullhandler for logging.
    """

    def emit( self, record ):
        pass

### define logger
logger = logging.getLogger( "dbc."+__name__ )
logger.addHandler( NullHandler() )


class TocTree( object ):
    """
    Class used to build a rst toctree
    """

    def __init__( self, header ):
        """
        Initializes Toctree.

        :param header:
            The header of the toctree
        :type header:
            string
        """
        self.xml = etree.Element( 'toc' )
        self.header = header

    def add( self, path ):
        """
        Adds path to Toctree. The section delimiter is '/'.

        :param path:
            Path to add to toctree
        :type path:
            string
        """
        parent = self.xml
        parts = ['toc'] + path.split( '/' )
        current = ""

        logger.debug( "rst Parts '%s'"%str( parts ) )
        for i, part in enumerate( [x for x in parts if x != ''] ):

            current += "/" + part
            logger.debug( "Current %s"%current )
            node = self.xml.xpath( current )

            if node:
                parent = node[0]
            else:
                elem = etree.Element( part )
                parent.append( elem )
                parent = elem

    def to_rst( self ):
        """ Returns rst string representation of toctree.
        """
        str_lst = []
        for node in self.xml.iter():
            depth = len( [x for x in node.iterancestors()] )
            if depth == 0:
                str_lst += [ self.header, '=' * len( self.header ), '' ]
            else:
                indent = '  ' * depth
                if len( node ) == 0:
                    str_lst += [  "%s* :doc:`%s`"%( indent, node.tag ), '' ]
                else:
                    str_lst += [  "%s* %s"%( indent, node.tag ), '' ]

        return "\n".join( str_lst )


def _create_rst( test, parser, nsmap ):
    """
    Creates a rst string for a single test result.

    :param test:
       test result to base rst on.
    :type test:
       dict
    :param parser:
        xml parser
    :type parser:
        lxml.etree.parser
    :param nsmap:
        namespace for parsing xml
    :type nsmap:
        dict.
    """
    xml = etree.parse( io.BytesIO( test['xml'] ), parser )

    def _retrieve_text( xpath ):
        result = xml.xpath( xpath, namespaces=nsmap )
        text = None
        if len( result ) > 0:
            text = result[0].text.strip()
        return text

    name = xml.xpath( '/wrapping/ts:test', namespaces=nsmap )[0].get( 'name' )
    fields = { 'description': _retrieve_text( '/wrapping/ts:test/ts:description' ),
               'given': _retrieve_text( '/wrapping/ts:test/ts:given' ),
               'when': _retrieve_text( '/wrapping/ts:test/ts:when' ),
               'then': _retrieve_text( '/wrapping/ts:test/ts:then' )}


    pretty_xml = "\n".join( ["   " + x for x in etree.tostring( xml, pretty_print=True, encoding="unicode" ).split( "\n" )] )

    rst = [ name, "-" * len( name ), "" ]

    for field in ['description', 'given', 'when', 'then' ]:
        if fields[field]:
            rst += [ "**%s:**"%field.capitalize(), "", fields[field], "" ]

    testsuite_name = 'testsuite: %s'%os.path.split( test['test-suite'] )[-1]

    rst += [ "``%s``"%testsuite_name, "" ]
    rst += [ '.. code-block:: xml', "", pretty_xml ]

    def convert( string ):
        #if type(string) == str:
        #    return string.encode( 'utf-8' )
        return string

    rst = list(map( convert, rst ))

    return ( name, "\n".join( rst ) )


def _create_treeview( rst, header ):
    """ Creates treeview of test results
    """
    logger.debug( "Creating tree view" )
    path_prefix = os.path.commonprefix( [x[0] for x in list(rst.keys())] )
    prefix_lst = [( x[0][len( path_prefix):], x ) for x in list(rst.keys())]
    toc = TocTree( header )
    for entry in prefix_lst:
        mod_entry = "/".join( entry[0].split( "/" )[:-1] ) + "/" + rst[entry[1]][0]
        logger.debug( "Adding entry '%s'->'%s'"%( entry, mod_entry ) )
        toc.add( mod_entry )

    return toc.to_rst()


def _create_flatview( rst, header ):
    """ Creates flatview of test results
    """
    logger.debug( "Creating flat view" )
    flatview = [ header ]
    flatview += [ "=" * len( header ), "" ]
    flatview += [ ".. toctree::", "   :maxdepth: 2", "" ]

    for key, value in rst.items():
        flatview += [ "   " + value[0] ]
    flatview += [ "" ]

    return "\n".join( flatview )


def _create_index( rst, type_name, start, delta ):
    """ Creates index page string
    """
    logger.debug( "Creating index %s, %s, %s", start, delta, delta_str( delta ) )
    index  = [ "Testrun: %s"%type_name ]
    index += [ "=" * len( index[0] ), "", "**Summary:**", "" ]
    index += [ "* Number of tests: %s"%len( list(rst.keys()) ) ]
    index += [ "* Build time: %s"%"%s-%s-%s %s:%s:%s"%(start.year, start.month, start.day,
                                                       start.hour, start.minute, start.second ) ]
    index += [ "* Build duration: %s"%delta_str( delta ), "" ]
    index += [ ".. toctree::", "    :maxdepth: 1", "" ]
    index += [ "    treeview", "    flatview", "" ]
    return "\n".join( index )


def create_test_documentation( test_results, folder, start_time, delta ):
    """
    Creates rst report based on test_results and places files in folder.

    :param test_results:
        test results
    :type test_results:
        list
    :param start_time:
        Build time for test
    :type start_time:
        datetime.datetime
    :param delta:
        Build duration
    :type delta:
        datetime.delta
    """
    logger.debug( "Creating test documentation" )

    def write_file( fname, content ):
        fh = open( fname, 'w' )
        fh.write( content )
        fh.close()

    parser = etree.XMLParser( remove_blank_text=True, encoding="UTF-8" )
    nsmap = { 'ts': "info:testsuite#" }

    rst = dict()

    for test in test_results:

        ( name, string ) = _create_rst( test, parser, nsmap )
        rst[ ( test['test-suite'], name ) ] = ( os.path.split( test['build-folder'] )[-1], string )

    if not os.path.exists( folder ):
        os.mkdir( folder )

    for key, value in rst.items():
        fname = os.path.join( folder, value[0] + '.rst' )
        write_file( fname, value[1] )

    fname = os.path.join( folder, 'treeview.rst' )
    write_file( fname, _create_treeview( rst, 'Tree View' ) )

    fname = os.path.join( folder, 'flatview.rst' )
    write_file( fname, _create_flatview( rst, 'Flat View' ) )

    fname = os.path.join( folder, 'index.rst' )

    write_file( fname, _create_index( rst, test_results[0]['type-name'], start_time, delta ) )
