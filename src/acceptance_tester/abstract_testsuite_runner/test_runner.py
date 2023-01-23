#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""
:mod:`acceptance_tester.abstract_testsuite_runner.test_runner` -- Abstract test runner
======================================================================================

=====================
Test Runner Interface
=====================

This abstract test runner should be implemented by test runners. The
constructor provides lists that can be used to write test results
to. If these lists are used, the acceptance tester framework will
handle the synchronized output and analyzed result output.  If the
implemting class raises an error this is interpreted as an entry into
the errors list.

The following fields are provided by the constructor:

#. **id**

   A unique int id for this test.

#. **test_path**

   The path of the testfile containing this test.

#. **base_folder**

   The folder The testfile is placed in.

#. **errors**

   Error messages should be placed on this list. If this is
   used errors are picked up by the framework. (This also happens if
   implementing code raises).

#. **failures**

   Failure messages should be placed on this list. If this is
   used failures are picked up by the framework.

#. **output**

   Normal output messages should be placed on this list. If this is
   used these are picked up by the framework.

The method :meth:`TestRunner.save_logfile` is also provided. The
logfiles picked up by this method are archived by the framework.
"""
import logging
import os
from nose.tools import nottest
import shutil


class NullHandler( logging.Handler ):
    """ Nullhandler for logging.
    """

    def emit( self, record ):
        pass

### define logger
logger = logging.getLogger( "dbc." + __name__ )
logger.addHandler( NullHandler() )


class TestSuiteParser( object ):
    """ Parser for testsuite tags
    """

    def __init__( self ):

        self.namespace = ( 'ts', 'info:testsuite#' )
        self.ns = self.namespace[1]

        do_nothing = lambda x: ( [], [], [] )
        self.parser_functions = { "{%s}description"%self.ns: do_nothing,
                                  "{%s}given"%self.ns      : do_nothing,
                                  "{%s}when"%self.ns       : do_nothing,
                                  "{%s}then"%self.ns       : do_nothing }

        self.setup_functions = { "{%s}setup"%self.ns      : { "setup"   : do_nothing,
                                                              "shutdown": do_nothing },
                                 "{%s}test"%self.ns       : { "setup"   : do_nothing,
                                                              "shutdown": do_nothing } }


class TestRunner( object ):
    """
    Abstract testrunner. Should be implemented by a testrunner handler.
    """

    def __init__( self, test_path, id, logfolder ):
        """
        Initializes the testrunner.

        :param test_path:
            Path to testsuite file
        :type test_path:
            string
        :param id:
            A unique test identifier.
        :type id:
            int
        :param logfolder:
            Folder to place logfiles in for arvhival.
        :type logfolder:
            string
        """
        self.id = id
        self.test_path = test_path
        self.errors = []
        self.failures = []
        self.output = []
        self.base_folder = os.path.dirname( test_path )
        self.logfolder = logfolder
        self.shutdown_hooks = []
        self.parser_functions = {}
        self.setup_functions = {}

        ### init parser
        self.suite = TestSuiteParser()
        self.parser_functions.update( self.suite.parser_functions )
        self.setup_functions.update( self.suite.setup_functions )

    def save_service_logfiles(self, service, name):
        logger.debug("Getting %s logfiles"%name)
        logFiles = service.get_logfiles()
        logger.debug("Got logfiles %s"%logFiles)
        for logfile in logFiles:
            self.save_logfile(logfile, prefix=name + "_")

    def save_logfile( self, logfile, prefix=None):
        """
        Saves the logfile. The logfile is picked up and archived in a
        zipfile by the framework.

        :param logfile:
            File to archive.
        :type logfile:
            string.
        :param postfix:
            Optional postfix to append to filename.
        :type postfix:
            string.
        """
        dest = os.path.join(self.logfolder, os.path.basename(logfile))
        if prefix != None:
            dest = os.path.join(self.logfolder, prefix + os.path.basename(logfile))

        shutil.copy( logfile, dest )

    @nottest
    def run_test( self, test_xml, build_folder, resource_manager ):
        """
        Runs test.

        :param test_xml:
            The test xml node
        :type test_xml:
            lxml.etree.Element
        :param build_folder:
            Path to build folder for this test.
        :type build_folder:
            string
        :param resource_manager:
            A reference to this tests resource_manager.
        :type resource_manager:
           class

        """
        raise NotImplementedError( "Should be implemented by inheriter." )

    def parse( self, test_xml ):
        """
        """
        suite_node = test_xml.xpath( "/wrapping/*", namespaces=dict( [self.suite.namespace] ) )
        setup_node = test_xml.xpath( "/wrapping/ts:setup/*", namespaces=dict( [self.suite.namespace] ) )
        test_node = test_xml.xpath( "/wrapping/ts:test/*", namespaces=dict( [self.suite.namespace] ) )

        def parse_type( nodes ):
            for node in nodes:
                logger.debug( "Evaluation Node '%s'"%node.tag )
                if node.tag in self.setup_functions:
                    self.shutdown_hooks.append( [ self.setup_functions[node.tag]["shutdown"], self.save_logfile] )
                    self.setup_functions[node.tag]["setup"]( node )
                else:
                    self.failures.append( "Tag '%s' is not known."%node.tag )

        try:
            parse_type( suite_node )
            parse_type( setup_node )

            for node in test_node:

                if node.tag in self.parser_functions:
                    logger.debug( "Evaluation Node '%s'"%node.tag )
                    self.__update_out( *self.parser_functions[node.tag]( node ) )
                else:
                    self.failures.append( "Tag '%s' is not known."%node.tag )

        except:
            self.shutdown()
            raise

        self.shutdown()

    def shutdown( self ):
        """ Runs all functions added to 'self.shutdown_hooks'
        """
        for hook in self.shutdown_hooks:
            args = ()
            if len( hook ) > 1:
                args = tuple( hook[1:] )
            self.__update_out( *hook[0]( *args ) )

    def __update_out( self, output, failures, errors ):
        self.output += output
        self.failures += failures
        self.errors += errors
