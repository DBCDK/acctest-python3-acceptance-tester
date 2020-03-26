#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""
:mod:`acceptance_tester.framework.find_tests` -- functionfs for finding and validating tests
============================================================================================

==========
Find tests
==========

This module provides functionality for finding and validating
acceptance testsuites. The main function of this module is
find_valid_tests.

Baseclass for retrieving documentation fields for test-reports.

The return type for get_fields must be upheld.
"""
import logging
import os
import pkg_resources
from lxml import etree
from nose.tools import nottest

import validate_testsuite
from acceptance_tester.supported_test_types import TYPES as TYPES
import acceptance_tester.framework.load_testrunner


class NullHandler( logging.Handler ):
    """ Nullhandler for logging.
    """

    def emit( self, record ):
        pass
### define logger
logger = logging.getLogger( "dbc."+__name__ )

logger.addHandler( NullHandler() )


@nottest
def find_valid_tests( test_folders, testrunner_config ):
    """
    Find all valid tests in test_folder, and returns a tuple with
    three entrys: test type, test type name, and a list of tests.

    :param test_folder:
        Folder containing testsuite files
    :type test_folder:
        string

    :returns:
        tuple with with test_type, test_type_name, and a list of tests.
    """
    # ### Find valid test suites
    test_suites = []

    for folder in test_folders:
        test_suites += _find_testsuites( folder )

    #test_suites = _find_testsuites( test_folder )
    if len( test_suites ) == 0:
        return (None, None, None )

    test_type_name, test_type = _get_test_type( map( lambda x: x[1], test_suites ), testrunner_config )

    if not 'test-runner' in test_type:
        err_msg = "Type '%s' is missing a 'test-runner' entry."%test_type_name
        logger.error( err_msg )
        raise RuntimeError( err_msg )

    if 'xsd' in test_type:
        test_suites = _filter_non_valid_suites( test_suites, test_type )

    retrieved_tests = _get_tests( test_suites )
    return ( test_type, test_type_name, retrieved_tests )


@nottest
def _find_testsuites( path ):
    """
    Find all testsuites files recursively in path.
    A testsuite file is defined as a xml file that can be
    validated against the testsuite xsd.
    """
    xml_files = []
    if os.path.isfile( path ) and path.endswith( '.xml' ) :
        xml_files.append( os.path.abspath( path ) )
    for root, dirs, files in os.walk( path ):
        for dir in dirs:
            if dir.startswith( '.' ):
                dirs.remove( dir )
        for f in filter( lambda x: x.endswith( '.xml' ), files ):
            xml_files.append( os.path.abspath( os.path.join( root, f ) ) )

    test_suites = []
    for xml_file in xml_files:
        xml = validate_testsuite.validate_testsuite_file( xml_file )

        if xml:
            test_suites.append( ( xml_file, xml ) )

    if len( test_suites ) < 1:
        err_msg = "Found no testsuite files in path '%s'"%path
        logger.warning( err_msg )
        return []

    suitename_list = map( lambda x: x[0], test_suites )
    suitename_list.sort()
    logger.debug( "Found the following testsuite files:\n%s"%"\n".join( suitename_list ) )
    return test_suites


@nottest
def _get_test_type( test_suites, testrunner_config ):
    """ Returns the test type of the test suites
    """
    types = set()
    for suite in test_suites:
        root = suite.getroot()
        types.add( root.get( "type" ) )

    if len( types ) > 1:
        err_msg = "Found multiple test types in tests"
        logger.error( err_msg )
        raise RuntimeError( err_msg )

    type_name = types.pop()
    return ( type_name, acceptance_tester.framework.load_testrunner.load_testrunner( TYPES[type_name], testrunner_config ) )


def _filter_non_valid_suites( test_suites, test_type ):
    """ Filters tests that does not validate against the test_type xsd """
    test_type_schema = _get_schema( test_type['xsd'] )

    def _validate( schema, test_suite ):
        result = schema.validate( test_suite[1] )

        if not result:
            logger.info( "Could not validate testsuite file '%s'"%test_suite[0] )
            return False
        return True

    test_suites = filter(  lambda x: _validate( test_type_schema, x ), test_suites )

    if len( test_suites ) < 1:
        err_msg = "Found no valid testsuite files in path"
        logger.error( err_msg )
        raise RuntimeError( err_msg )
    return test_suites


def _get_schema( self, package_path ):
    """
    Returns schema file using pkg_resources. This works when the
    code called in the source tree, and when it is packaged in an
    egg file.
    """
    if not pkg_resources.resource_exists( 'acceptance_tester', package_path ):
        err_msg = "Could not find xsd file at package path '%s'"%package_path
        logger.error( err_msg )
        raise RuntimeError( err_msg )

    path = pkg_resources.resource_filename( 'acceptance_tester', package_path )
    schema = etree.XMLSchema( etree.parse( path ) )
    return schema


@nottest
def _get_tests( test_suites ):
    """ isolates all test nodes and wraps them with a 'wrapping' node with the tests setup node. """

    namespace = "{info:testsuite#}"
    doc_names = ["description", "given", "then", "when"]
    doc_names = map( lambda x: namespace + x, doc_names )
    tests = []

    ### These characters cannot be present in the name, as this
    ### value is used as xml node names and file paths
    banned_chars = [ '/', '.', '*', '@', ':', '(', ')', '[', ']', '+', ','  ]

    for suite in test_suites:
        root = suite[1].getroot()
        nodes = filter( lambda x: x.tag != etree.Comment, root )
        test_nodes = filter( lambda x: x.tag == "%stest"%namespace, nodes )

        #setup_node = filter( lambda x: x.tag == "%ssetup"%namespace, nodes )[0]
        #setup_str = etree.tostring( setup_nodes, pretty_print=True, encoding="UTF-8" )

        setup_nodes = filter( lambda x: x.tag == "%ssetup"%namespace, nodes )

        setup_str = None
        if len( setup_nodes ) > 0:

            setup_str = etree.tostring( setup_nodes[0], pretty_print=True, encoding="UTF-8" )

        for test in test_nodes:

            doc = {}
            for node in test:
                if node.tag in doc_names:
                    text = " ".join( map( lambda x: x.strip(),
                                          filter( lambda x: x != '', node.text.split( "\n" ) ) ) )
                    doc[node.tag[len(namespace):]] = text

            banned = None
            for char in banned_chars:
                if char in test.get( 'name' ):
                    banned = char
                    break
            if banned != None:

                err_msg = "'%s' cannot be used in test names (%s), because this "%( str( banned ), test.get('name') ) + \
                          "is also used as filenames/xml-nodes. Please rename test and try again."
                logger.error( err_msg )
                raise RuntimeError( err_msg )


            test_str = etree.tostring( test, pretty_print=True, encoding="UTF-8" )

            xml = "".join( [ "<wrapping name=\"%s\">" % test.get( "name" ), test_str, "</wrapping>" ] )
            if setup_str:
                xml = "".join( [ "<wrapping name=\"%s\">" % test.get( "name" ),
                                 setup_str, test_str, "</wrapping>" ] )

            tests.append( ( suite[0], test.get( "name" ), xml, doc ) )

    if len( tests ) < 1:
        err_msg = "Found no tests in testsuite files '%s'"%map(lambda x: x[0], test_suites )
        logger.error( err_msg )
        raise RuntimeError( err_msg )
    return tests
