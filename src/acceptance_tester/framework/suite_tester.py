#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""
:mod:`acceptance_tester.framework.suite_tester` -- Runs testsuites
==================================================================

============
Suite Tester
============

The suite tester contains the main framework for
acceptance-tester.

This module contains the class :class:`SuiteTester`. Besides the
constructor this class only exposes the run method.

A :class:`SuiteTester` instance can be created and run by using
the function :func:`run` found in this module.
"""
import logging
import multiprocessing
import os
import re
import shutil
import sys
import zipfile
from datetime import datetime
import io

from lxml import etree
from .aux import delta_str
from .aux import datetime_str
from . import job
from . import find_tests
sys.path.insert( 0, os.path.dirname( os.path.dirname( os.path.realpath( sys.argv[0] ) ) ) )
import acceptance_tester.framework.rst_creator as rst_creator

from dbc_python.utils.junit_testsuite import Junit_testsuite
from acceptance_tester._version import __version__
from dbc_python._version import __version__ as dbc_python__version__
from os_python._version import __version__ as os_python__version__


class NullHandler( logging.Handler ):
    """ Nullhandler for logging.
    """

    def emit( self, record ):
        pass
### define logger
logger = logging.getLogger( "dbc."+__name__ )

logger.addHandler( NullHandler() )


class SuiteTester( object ):
    """
    Executes and reports on acceptance test testsuite files.
    """

    def __init__( self,
                  paths_to_tests,
                  build_folder,
                  resource_folder,
                  test_results_folder,
                  report_file,
                  log_file,
                  testrunner_config,
                  pool_size,
                  verbose,
                  use_preloaded_resources,
                  use_configured_resources,
                  port_range="12000-13000",
                  color=False,
                  no_clean=False):
        """
        Initializes the testsuite runner.

        :param paths_to_tests:
            Path to testsuite files.
        :type paths_to_tests:
            list
        :param build_folder:
            The folder to to use for test builds.
            This is created if it does not exist.
        :type build_folder:
            string
        :param resource_folder:
            The folder used by the resource-manager.
            This is created if it does not exist.
        :type resource_folder:
            string
        :param test_results_folder:
            The folder to place test result files in.
            This is created if it does not exist.
        :type test_results_folder:
            string
        :param report_file:
            path to report file.
        :type report_file
            string
         :param log_file:
             Zipfile to place logs in.
        :type log_file
            string
        :param testrunner_config:
             file used to configure testrunner
        :type testrunner_config
            string
        :param pool_size:
            The size of the process pool.
        :type pool_size:
            int
        :param verbose:
            If true verbose output is printed to stdout
        :type verbose:
            boolean
        :param use_preloaded_resources:
            If true allows resource manager to use preloaded resources
        :type use_preloaded_resources:
            boolean
        :param use_configured_resources:
            None or path to configuration file containing paths to resources.
        :type use_configured_resources:
            boolean
        :param port_range:
            if specified the ResourceManager will use this range to
            allocate ports in. default is '12000-13000'
        :type port_range:
            tuple with two int elements
        :param color:
            If true, ansi escape codes are used to colorize output.
        :type color:
            Boolean

        :raise RuntimeError:
            If arguments are not good enough for starting test runner.
        """
        logger.debug( "acceptance-tester version: '%s'"%__version__ )
        logger.debug( "dbc-python version: '%s'"%dbc_python__version__ )
        logger.debug( "os-python version: '%s'"%os_python__version__ )
        logger.info( "Initializing test environment." )
        self.start = datetime.now()

        self.log_file = os.path.abspath( log_file )
        self.testrunner_config =  testrunner_config
        self.verbose = verbose
        self.use_preloaded_resources = use_preloaded_resources
        self.use_configured_resources = use_configured_resources

        self.color = color

        self.report_file = os.path.abspath( report_file )
        self.paths_to_tests = list(map( os.path.abspath, paths_to_tests ))

        self.pool_size = self._validated_pool_size( pool_size )
        self.port_range = self._validated_port_range( port_range )

        self.parser = etree.XMLParser( remove_blank_text=True, encoding="UTF-8" )

        self._write_lines( "Acceptance test started - %s"%datetime_str( self.start ), force_print=True )

        self.test_type, self.test_type_name, retrieved_tests = find_tests.find_valid_tests( self.paths_to_tests, self.testrunner_config )

        if retrieved_tests == None:
            logger.debug( "Found no testfiles" )
            return

        ### create needed folders
        self.build_folder = self._create_folder( build_folder )
        self.log_folder = self._create_folder( os.path.join( build_folder, 'logs' ) )
        self.test_results_folder = self._create_folder( test_results_folder )
        self.resource_folder = self._create_folder( resource_folder )

        ### create job arguments dictionary
        self.tests = []
        for i, case in enumerate( retrieved_tests ):

            test_arguments = dict()
            test_arguments['build-folder'] = self._create_folder_name( case[0], case[1] )
            test_arguments['log-folder'] = self.log_folder
            test_arguments['name'] = case[1]
            test_arguments['documentation'] = case[3]
            test_arguments['id'] = i
            test_arguments['report-file'] = self.report_file
            test_arguments['test-suite'] = case[0]
            test_arguments['type'] = self.test_type
            test_arguments['type-name'] = self.test_type_name
            test_arguments['verbose'] = self.verbose
            test_arguments['xml'] = case[2]
            test_arguments['color'] = self.color
            test_arguments['no_clean'] = no_clean
            
            self.tests.append( test_arguments )

        self.number_of_tests = len( self.tests )
        self.number_of_testsuites = len( set( [x['test-suite'] for x in self.tests] ) )
        self.delimiter_length = 120
        ### Create status log message
        self._write_lines( self.__create_initialization_status_lines() )

    def _validated_pool_size( self, pool_size ):
        pool_size = int( pool_size )
        if pool_size < 1:
            err_str = "Pool size must be larger than 1. Given poolsize '%s'"%pool_size
            logger.error( err_str )
            raise RuntimeError( err_str )
        return pool_size

    def _validated_port_range( self, port_range ):
        spl = port_range.split( "-" )
        if len( spl ) != 2 or int( spl[0] ) >= int( spl[1] ):
            err_str = "Unknown portrange format in string '%s', "%port_range + \
                      "format is: start-end, where start and end are integers and start is smaller than end"
            logger.error( err_str )
            raise RuntimeError( err_str )
        port_range = ( int( spl[0] ), int( spl[1] ) )
        return port_range

    def run( self ):
        """
        Executes tests identified during construction.

        An appropriate resource manager is initialized, and the tests
        are processed in a process pool. Afterwards the results are
        analysed and logged.
        """
        try:
            if self.test_type == None:
                self._write_lines( "Found no tests... exiting.", force_print=True )
                self._write_junit_files( [] )
                return

            self.resource_manager = None
            if 'resource-manager' in self.test_type:
                self.resource_manager = self.test_type['resource-manager']( self.resource_folder,
                                                                            self.tests,
                                                                            self.use_preloaded_resources,
                                                                            self.use_configured_resources,
                                                                            self.port_range )
            self._write_lines( "Creating pool, and starting tests" )

            for test in self.tests:
                test['resource-manager'] = self.resource_manager

            ### run tests

            pool = multiprocessing.Pool( self.pool_size )
            results = pool.map( job.job, self.tests )
            pool.close()
            pool.join()
        finally:
            if hasattr(self, "resource_manager") and self.resource_manager is not None:
                self.resource_manager.shutdown()

        ### analyze results
        delta = datetime.now() - self.start
        self._zip_logs()
        self._write_junit_files( results )
        self._write_lines( self.__create_summary_of_tests_lines( results ) )
        self._write_lines( self.__create_summary_lines( results, delta ), True )
        rst_creator.create_test_documentation( results,
                                               os.path.join( self.test_results_folder, "sphinx-rst" ),
                                               self.start, delta )

    def _create_folder( self, folder ):
        """ Creates folder if does not already exist, and return an absolute path to folder."""
        mod = os.path.abspath( folder )
        if not os.path.exists( mod ):
            logger.debug( "Creating Folder" )
            os.mkdir( mod )
        return mod

    def _create_folder_name( self, suite_file, test_name ):
        """ Create folder name based on the testsuite filename and the testname """
        sname = suite_file.split( os.sep )[-1]
        sname = sname[:sname.rfind( '.' )] # remove suffix
        tname = re.sub( "\s", "_", test_name ) # replace whitespaces
        fname = os.path.join( self.build_folder, "%s___%s"%( sname, tname ) )
        return fname

    def _zip_logs( self ):
        logger.debug( "zipping logs found in folder '%s' into file '%s'"%( self.log_folder, self.log_file ) )
        zfile = zipfile.ZipFile( self.log_file, 'w', zipfile.ZIP_DEFLATED )

        for root, dirs, files in os.walk( self.log_folder ):
            for f in files:
                zfile.write( os.path.join( root, f ),
                             os.path.join( 'logs', os.path.split( root )[-1], f ) )
        zfile.close()
        shutil.rmtree( self.log_folder )

    def _write_junit_files( self, results ):
        """
        Generates and writes test result files for each testsuite.
        """
        parsed_results = dict()

        parser = etree.XMLParser( remove_blank_text=True, encoding="UTF-8" )
        nsmap = { 'ts': "info:testsuite#" }

        for result in results:

            if not result['test-suite'] in parsed_results:
                parsed_results[result['test-suite']] = [ result ]
            else:
                parsed_results[result['test-suite']].append( result )
        for name, data in parsed_results.items():

            mod_name = [x for x in name.split( os.sep ) if x != '']
            mod_name[-1] = mod_name[-1][:mod_name[-1].rfind( '.' )]
            fullname = ".".join( mod_name )
            self._create_folder( os.path.join( self.test_results_folder, "xUnit" ) )

            filename = os.path.join( self.test_results_folder, "xUnit", "TEST-%s.xml"%".".join( mod_name ) )
            ### Shorten name if testfile is in subfolder of 'testsuites'
            if 'testsuites' in mod_name:
                mod_name = mod_name[mod_name.index( 'testsuites' ) + 1:]

            suite_path = ".".join( mod_name )
            logger.debug( "Writing testsuite file '%s'"%filename )
            junit_xml = Junit_testsuite( fullname )

            for i, test in enumerate(data):
                xml = etree.parse( io.StringIO( test['xml'] ), parser )
                def _retrieve_text( xpath ):
                    result = xml.xpath( xpath, namespaces=nsmap )
                    text = None
                    if len( result ) > 0:
                        text = result[0].text.strip()
                    return text

                description = _retrieve_text( '/wrapping/ts:test/ts:description')
                given = _retrieve_text( '/wrapping/ts:test/ts:given')
                when = _retrieve_text( '/wrapping/ts:test/ts:when')
                then = _retrieve_text( '/wrapping/ts:test/ts:then')

                msg = "\nDescription:\n%s\n\nGiven:\n%s\n\nWhen:\n%s\n\nThen:\n%s\n"%( description, given, when, then )
                junit_xml.set_system_out(msg)

                name = str(i) + "_" + test['name'].replace(' ', '_').replace('-', '_').replace(',', '_')
                if len( test['errors'] ) > 0:
                    junit_xml.add_error( suite_path, name, test['time'], "\n".join( test['errors'] ) )
                elif len( test['failures'] ) > 0:
                    junit_xml.add_failure( suite_path, name, test['time'], "\n".join( test['failures'] ) )
                else:
                    junit_xml.add_success( suite_path, name, test['time'] )

            junit_xml.write( filename )

    def _write_lines( self, lines, force_print=False ):
        """
        Logs and writes line or lines to report_file, if verbose
        is true, line or lines are also printed to stdout
        """
        fh = open( self.report_file, 'a' )

        if type( lines ) == str:
            fh.write( "%s\n"%lines )
            logger.info( lines )
            if self.verbose or force_print:
                print(lines)

        else:
            for line in lines:
                fh.write( "%s\n"%line )
                logger.info( line )
                if self.verbose or force_print:
                    print(line)
        fh.close()

    ########################################################################################################################
    ### Pretty print functions
    ###
    def __create_initialization_status_lines( self ):

        header = []
        header.append( ( "test paths", str( self.paths_to_tests ) ) )
        header.append( ( "build folder", self.build_folder ) )
        header.append( ( "resource folder", self.resource_folder ) )
        header.append( ( "report file", self.report_file ) )
        header.append( ( "test result folder", self.test_results_folder ) )
        header.append( ( "pool size", self.pool_size ) )
        header.append( ( "test type", self.test_type_name ) )
        header.append( ( "number of tests", self.number_of_tests ) )
        header.append( ( "number of testsuite files", self.number_of_testsuites ) )
        header.append( ( "test runner", self.test_type['test-runner'] ) )
        if 'resource-manager' in self.test_type:
            header.append( ( "resource manager", self.test_type['resource-manager'] ) )
        if 'xsd' in self.test_type:
            header.append( ( "xsd file", self.test_type['xsd'] ) )
        offset = max( [len( x[0] ) for x in header] ) + 5
        func_ppad = lambda s, l: s + ( "." * ( l - len( s ) ) )
        header = ["%s %s"%( func_ppad( x[0] + ":", offset ), x[1] ) for x in header]

        header.insert( 0, "="*self.delimiter_length )
        header.insert( 1, "Acceptance-tester initialized:" )
        header.insert( 2, "" )
        header.append( "="*self.delimiter_length )
        return header

    def __create_summary_lines( self, results, delta ):

        if self.color:
            try:
                import colorama
            except ImportError:
                logger.error( "Could not load colorama module. Colorized output disabled" )
                self.color = False

        if self.color:
            colorama.init()

        summary = [ "=" * self.delimiter_length,
                    "Ran %s tests found in %s testfiles."%( self.number_of_tests,
                                                            self.number_of_testsuites) ]

        errors = sum( [x['status'] == "ERROR" for x in results] )
        failures = sum( [x['status'] == "FAILURE" for x in results] )

        prec = postc = ""
        if errors > 0:
            if self.color:
                prec = colorama.Fore.RED+colorama.Style.BRIGHT
                postc = colorama.Fore.RESET+colorama.Style.RESET_ALL
            summary.append( "%s tests caused %sERRORS%s"%( errors, prec, postc ) )

        if failures > 0:
            if self.color:
                prec = colorama.Fore.YELLOW+colorama.Style.BRIGHT
                postc = colorama.Fore.RESET+colorama.Style.RESET_ALL
            summary.append( "%s tests %sFAILED%s"%( failures, prec, postc ) )
        if errors == 0 and failures == 0:
            if self.color:
                prec = colorama.Fore.GREEN+colorama.Style.BRIGHT
                postc = colorama.Fore.RESET+colorama.Style.RESET_ALL
            summary.append( "All tests ran %sSUCCESSFULLY%s"%( prec, postc ) )
        summary += ["", "Duration: %s"%delta_str( delta ),
                    "=" * self.delimiter_length ]
        logger.debug( "[PERFORMANCE:(test-suite-duration, sum, %s)]"%delta )
        return summary

    def __create_summary_of_tests_lines( self, results ):

        summary = [ '', "="*self.delimiter_length, 'Test Summarys:', '--------------', '' ]
        for result in results:
            summary += result['summary'][1:] + ['']
        return summary


def run( test_paths, build_folder, resource_folder, test_result_folder, report_file, log_file, testrunner_config, pool_size, verbose, use_preloaded_resources, use_configured_resources, port_range, color, no_clean ):
    """
        Initializes and runs a testsuite runner.

        :param test_paths:
            Paths to testsuite files.
        :type test_paths:
            list
        :param build_folder:
            The folder to to use for test builds.
            This is created if it does not exist.
        :type build_folder:
            string
        :param resource_folder:
            The folder used by the resource-manager.
            This is created if it does not exist.
        :type resource_folder:
            string
        :param test_results_folder:
            The folder to place test result files in.
            This is created if it does not exist.
        :type test_results_folder:
            string
        :param log_file:
             Zipfile to place logs in.
        :type log_file
            string
        :param pool_size:
            The size of the process pool.
        :type pool_size:
            int
        :param verbose:
            If true verbose output is printed to stdout
        :type verbose:
            boolean
        :param use_preloaded_resources:
            If true allows resource manager to use preloaded resources
        :type use_preloaded_resources:
            boolean
        :param port_range:
            if specified the ResourceManager will use this range to
            allocate ports in.
        :type port_range:
            tuple with two int elements
        :param color:
            If true, ansi escape codes are used to colorize output.
        :type color:
            Boolean
    """
    tsr = SuiteTester( test_paths,
                       build_folder,
                       resource_folder,
                       test_result_folder,
                       report_file,
                       log_file,
                       testrunner_config,
                       pool_size,
                       verbose,
                       use_preloaded_resources,
                       use_configured_resources,
                       port_range,
                       color,
                       no_clean)

    tsr.run()
