#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""
:mod:`acceptance_tester.framework.job` -- Wraps each testrun
============================================================

===========
Job wrapper
===========

This module contains the :func:`job` functions which is used to
wrap each test. The wrapper provides timming and reporting of test
run, and any errors thrown by the individual test is handled.

The test is executed with the
:class:`acceptance_tester.abstract_testsuite_runner.test_runner` compliant
class pointed to by the test type.
"""
import fcntl
import threading
import logging
import os
import shutil
import sys
import time
from datetime import datetime
from lxml import etree

sys.path.insert( 0, os.path.split( os.path.dirname( os.path.realpath( sys.argv[0] ) ) )[0] )
sys.path.insert( 0, os.path.dirname( os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath( sys.argv[0] ) ) ) ) ) )

from aux import delta_str
from aux import datetime_str
from aux import format_description


class NullHandler( logging.Handler ):
    """
    Nullhandler for logging.
    """

    def emit( self, record ):
        pass

### define logger
logger = logging.getLogger( "dbc."+__name__ )
logger.addHandler( NullHandler() )

stdout_lock = threading.Lock()


def _sync_file_append( path, string ):
    """
    Writes string in to file in thread-safe manner.
    Blocks until lock on file at path is obtained. afterwards the string
    is written, the file is closed and the lock is released.

    :param path:
        Path to file to append to.
    :type path:
        string
    :param string:
        String to append to file at path.
    :type:
        string
    """
    outfile = open( path, 'a' )
    fcntl.lockf( outfile.fileno(), fcntl.LOCK_EX )

    outfile.write( string )

    fcntl.lockf( outfile.fileno(), fcntl.LOCK_UN )
    outfile.close()


def _sync_stdout_write( string ):
    """
    Writes string in thread-safe manner.
    Blocks until lock on sys.stdout is obtained. afterwards the string
    is written and the lock is released.

    :param string:
        String to write to stdout.
    :type:
        string
    """
    #fcntl.lockf( sys.stdout.fileno(), fcntl.LOCK_EX )
    stdout_lock.acquire()
    sys.stdout.write( string + "\n" )
    stdout_lock.release()
    #fcntl.lockf( sys.stdout.fileno(), fcntl.LOCK_UN )


def _make_folder( candidate_name ):
    """
    Creates folder based on candidate_name.  If candidate_name exists,
    a new candidate_name is created by appending suffix. This process
    is continued until unused folder name is found, and a fresh folder
    is created and returned.
    :param candidate_name:
        Candidate filepath name.
    :type candidate_name:
        string
    :return:
        Path to folder
    """
    name = candidate_name
    index = 1
    while os.path.exists( name ):
        name = candidate_name + "_" + str( index )
        index += 1
    logger.debug( "Creating folder '%s'"%name )
    os.mkdir( name )
    return name


def _generate_summary( filename, testname, testcase, delta ):
    """
    Generates test summary for the result of the test.

    :param filename:
        Testsuite filename
    :type filename:
        string
    :param testname:
        Name of the test
    :type testname:
        string
    :param testcase:
        testcase after test is run.
    :type testcase:
        type as specified in :data:`TESTCASE`
    :param delta:
        running time of the test.
    :type delta:
        datetime.delta

    :return:
        Tuple with two elements:

        1. Short status string.
        2. Test summary.
    """
    status = None
    status_msg = None
    summary = ["Test Summary:"]
    summary.append( "  testfile: '%s'"%filename)
    summary.append( "  testname: '%s'"%testname )

    if len( testcase.errors ) > 0:
        summary.append( "  status: ERROR" )
        summary += [""] + testcase.errors + [""]
        status_msg = "Test '%s' status: ERROR."%testname
        status = "ERROR"
    elif len( testcase.failures ) > 0:
        summary.append( "  status: FAILED" )
        summary += [""] + testcase.failures + [""]
        status_msg = "Test '%s' status: FAILED."%testname
        status = "FAILURE"
    else:
        summary.append( "  status: SUCCESS" )
        status_msg = "Test '%s' status: SUCCESS."%testname
        status = "SUCCESS"

    logger.debug( "[PERFORMANCE:(test-duration-avg, avg, %s)]"%delta )
    summary.append( "  duration: %s"%delta_str( delta ) )
    summary.insert( 0, "-"*13 )
    summary.append( "-"*120 )
    return ( status, status_msg, summary )


def _format_traceback( exc_info, error ):
    """
    Formats a traceback string from exc_info as retrieved by
    sys.exc_info() and the specific errror which caused the traceback.

    :param exc_info:
        Tuple as retrieved through sys.exc_info().
    :type exc_info:
        tuple
    :param error:
        Error to retrieve type and message from.
    :type error:
        Exception
    :return:
        Formatted traceback as a string.
    """
    import traceback
    exc_tb = traceback.extract_tb( exc_info[2] )
    tb = traceback.format_list( exc_tb )
    tb = map( lambda x: [x], tb )

    formatted_traceback = []
    for entry in tb:
        for fentry in filter( lambda x: x != '', entry[0].split( "\n" ) ):
            formatted_traceback.append( fentry )

    formatted_traceback.insert( 0, "Traceback (most recent call last):" )
    formatted_traceback.append( "%s: %s"%( error.__class__.__name__, str( error ) ) )
    return "\n".join( formatted_traceback )


def _remove_build_folder( folder ):
    """
    """
    try:
        shutil.rmtree( folder )
        removed = True
    except OSError, e:
        logger.warning( "Unable to remove build folder: %s"%e )
        # Try again, then fail
        time.sleep( 1 )
        shutil.rmtree( folder )


def job( test ):
    """
    Wraps a testcase run.

    This function handles report file writing, and stdout output. it
    also provide timings.

    :param test:
        A dictionary where the following entrys must be present:

        #. **build-folder**

           Folder for test to place build files in.

        #. **log-folder**

           Folder to place logfiles in for archival.

        #. **id**

           The test id (int).

        #. **name**

           The name of the test.


        #. **report-file**

           The report file to write to.

        #. **test-suite**

           The path to the testsuite file containing this test.

        #. **type**

           The type dictionary for the test type

        #. **type-name**

           Name of the test type.

        #. **verbose**

           Boolean flag indictaing verbosity. If true extra info is
           written to stdout.

        #. **xml**

           The test xml as a string (etree.lxml.Element is not
           picklable).

    :type test:
        dict


    :return:

        Dictionary with the following content.

        #. **errors**

           List containing error messages from testrun.

        #. **failures**

           List containing failure messages from testrun.

        #. **name**

           The name of the test.

        #. **status**

           The status of testrun. Can be (ERROR|FAILURE|SUCCESS).

        #. **status-msg**

           Status message.

        #. ***summary**

           A summary of the testrun.

        #. **test-suite**

           The path to the testsuite file containing this test.

        #. **build-folder**

           The path to the tests buidl-folder

    :rtype:
       dict
    """
    color = test['color']
    if color:
        try:
            import colorama
        except ImportError:
            logger.error( "Could not load colorama module. Colorized output disabled" )
            color = False

    # setup
    start = datetime.now()
    test_output = []
    test['build-folder'] = _make_folder( test['build-folder'] )
    logfolder = os.path.join( test['log-folder'], os.path.split( test['build-folder'] )[-1] )
    if not os.path.exists( logfolder ):
        os.mkdir( logfolder )
    parser = etree.XMLParser( remove_blank_text=True, encoding="UTF-8" )
    xml = etree.fromstring( test['xml'], parser )

    _sync_stdout_write( "Starting Test '%s'"%test['name'] )

    logger.info( "Starting Test '%s'."%test['name'] )
    logger.debug( "Initializing testcase runner" )

    testcase_runner = test['type']['test-runner']( test['test-suite'], test['id'], logfolder )

    desc = ""
    if 'documentation' in test and 'description' in test['documentation']:
        try:
            desc = format_description( test['documentation']['description'] )
        except Exception, err:
            exc_info = sys.exc_info()
            tb = _format_traceback( exc_info, err )
            testcase_runner.errors.append( tb )
            logger.error( tb )

    prec = postc = ""
    if color:
        prec = colorama.Style.BRIGHT
        postc = colorama.Style.RESET_ALL

    output = "-" * 120 +"\nStarted Test '%s%s%s' at %s\n\n"%( prec, test['name'], postc, datetime_str( start ) )
    if desc:
        output += "%s\n"%desc

    ### run test

    try:
        testcase_runner.run_test( xml,
                                  test['build-folder'],
                                  test['resource-manager']  )
    except Exception, err:
        exc_info = sys.exc_info()
        tb = _format_traceback( exc_info, err )
        testcase_runner.errors.append( tb )
        logger.error( tb )

    if testcase_runner.errors:
        testcase_runner.errors.insert(0, "Testname : '%s'" % test['name'])
    if testcase_runner.failures:
        testcase_runner.failures.insert(0, "Testname : '%s'" % test['name'])

    if not 'no_clean' in test or not test['no_clean']:
        _remove_build_folder( test['build-folder'] )

    # write output and summary
    delta = datetime.now() - start
    test_output += [""] + testcase_runner.output
    ( status, status_msg, summary ) = _generate_summary( test['test-suite'], test['name'], testcase_runner, delta )
    test_output += summary + [""]
    _sync_file_append( test['report-file'], "\n".join( test_output ) )

    output += status_msg

    if test['verbose']:
        output += "\n".join( test_output )

    if color:
        output = colorize( output )
        summary = map( colorize, summary )

    _sync_stdout_write( output )

    xml_str = etree.tostring( xml, pretty_print=True, encoding="UTF-8" )
    #xml_str = xml_str.decode( 'UTF-8' )
    return { 'name': test['name'],
             'documentation': test['documentation'],
             'test-suite': test['test-suite'],
             'failures': testcase_runner.failures,
             'errors': testcase_runner.errors,
             'time': delta,
             'id': test['id'],
             'summary': summary,
             'status-msg': status_msg,
             'status': status,
             'build-folder': test['build-folder'],
             'type-name': test['type-name'],
             'xml': xml_str }


def colorize( string ):

    import colorama
    patterns = { 'ERROR': [ colorama.Fore.RED+colorama.Style.BRIGHT, colorama.Fore.RESET+colorama.Style.RESET_ALL ],
                 'FAILED': [ colorama.Fore.YELLOW+colorama.Style.BRIGHT, colorama.Fore.RESET+colorama.Style.RESET_ALL ],
                 'SUCCESS': [ colorama.Fore.GREEN+colorama.Style.BRIGHT, colorama.Fore.RESET+colorama.Style.RESET_ALL ] }

    for pattern, codes in patterns.iteritems():
        string = string.replace( pattern, codes[0] + pattern + codes[1] )

    return string
