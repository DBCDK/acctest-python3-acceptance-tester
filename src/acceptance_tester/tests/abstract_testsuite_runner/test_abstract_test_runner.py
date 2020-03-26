
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
import os
import unittest
import shutil
import tempfile
from lxml import etree
from mock import Mock

import acceptance_tester.abstract_testsuite_runner.test_runner as testrunner


class TestSuiteTester( unittest.TestCase ):

    def setUp( self ):
        self.test_folder = tempfile.mkdtemp()
        self.logfolder = os.path.join( self.test_folder, 'logfolder' )

    def tearDown( self ):
        shutil.rmtree( self.test_folder )

    def test_parser_unknown_setup_node_result_in_failure( self ):
        """ test whether a unknown setup node results in a failure as expected
        """
        testsuite = '''<wrapping name="facet genreCategory">
                        <setup xmlns="info:testsuite#"
                               xmlns:s="http://dbc.dk/xml/namespaces/solr">
                         <s:foo type="normal"/>
                        </setup>
                        <test xmlns="info:testsuite#"
                              xmlns:s="http://dbc.dk/xml/namespaces/solr"
                              name="facet genreCategory">
                        </test>
                       </wrapping>'''


        tr = testrunner.TestRunner( 'testpath', 1, self.logfolder )
        tr.parse( etree.fromstring( testsuite ) )
        self.assertEqual( tr.failures, ["Tag '{http://dbc.dk/xml/namespaces/solr}foo' is not known."] )

    def test_parser_unknown_test_node_result_in_failure( self ):
        """ test whether a unknown test node results in a failure as expected
        """
        testsuite = '''<wrapping name="facet genreCategory">
                        <setup xmlns="info:testsuite#"
                               xmlns:s="http://dbc.dk/xml/namespaces/solr">
                        </setup>
                        <test xmlns="info:testsuite#"
                              xmlns:s="http://dbc.dk/xml/namespaces/solr"
                              name="facet genreCategory">
                         <s:bar/>
                        </test>
                       </wrapping>'''

        tr = testrunner.TestRunner( 'testpath', 1, self.logfolder )
        tr.parse( etree.fromstring( testsuite ) )
        self.assertEqual( tr.failures, ["Tag '{http://dbc.dk/xml/namespaces/solr}bar' is not known."] )

    def test_parser_node_function_out_is_present_in_output( self ):
        """ test whether a node function adding info to out is present in the final output
        """
        testsuite = '''<wrapping name="facet genreCategory">
                        <setup xmlns="info:testsuite#"
                               xmlns:s="http://dbc.dk/xml/namespaces/solr">
                        </setup>
                        <test xmlns="info:testsuite#"
                              xmlns:s="http://dbc.dk/xml/namespaces/solr"
                              name="facet genreCategory">
                         <s:myfunc/>
                        </test>
                       </wrapping>'''

        def myfunc( node ):
            return ( ['TEST-OUTPUT'], [], [] )

        tr = testrunner.TestRunner( 'testpath', 1, self.logfolder )
        tr.parser_functions.update( {'{http://dbc.dk/xml/namespaces/solr}myfunc': myfunc} )
        tr.parse( etree.fromstring( testsuite ) )

        self.assertEqual( tr.output, ['TEST-OUTPUT'] )

    def test_parser_node_function_fail_is_present_in_output( self ):
        """ test whether a node function adding info to fail is present in the final output
        """
        testsuite = '''<wrapping name="facet genreCategory">
                        <setup xmlns="info:testsuite#"
                               xmlns:s="http://dbc.dk/xml/namespaces/solr">
                        </setup>
                        <test xmlns="info:testsuite#"
                              xmlns:s="http://dbc.dk/xml/namespaces/solr"
                              name="facet genreCategory">
                         <s:myfunc/>
                        </test>
                       </wrapping>'''

        def myfunc( node ):
            return ( [], ['TEST-FAIL'], [] )

        tr = testrunner.TestRunner( 'testpath', 1, self.logfolder )
        tr.parser_functions.update( {'{http://dbc.dk/xml/namespaces/solr}myfunc': myfunc} )
        tr.parse( etree.fromstring( testsuite ) )

        self.assertEqual( tr.failures, ['TEST-FAIL'] )

    def test_parser_node_function_error_is_present_in_output( self ):
        """ test whether a node function adding info to out is present in the final output
        """
        testsuite = '''<wrapping name="facet genreCategory">
                        <setup xmlns="info:testsuite#"
                               xmlns:s="http://dbc.dk/xml/namespaces/solr">
                        </setup>
                        <test xmlns="info:testsuite#"
                              xmlns:s="http://dbc.dk/xml/namespaces/solr"
                              name="facet genreCategory">
                         <s:myfunc/>
                        </test>
                       </wrapping>'''

        def myfunc( node ):
            return ( [], [], ['TEST-ERROR'] )

        tr = testrunner.TestRunner( 'testpath', 1, self.logfolder )
        tr.parser_functions.update( {'{http://dbc.dk/xml/namespaces/solr}myfunc': myfunc} )
        tr.parse( etree.fromstring( testsuite ) )

        self.assertEqual( tr.errors, ['TEST-ERROR'] )

    def test_parser_shutdown_is_called( self ):
        """ test whether shutdown is called if a node fuinction raises
        """
        testsuite = '''<wrapping name="facet genreCategory">
                        <setup xmlns="info:testsuite#"
                               xmlns:s="http://dbc.dk/xml/namespaces/solr">
                        </setup>
                        <test xmlns="info:testsuite#"
                              xmlns:s="http://dbc.dk/xml/namespaces/solr"
                              name="facet genreCategory">
                        </test>
                       </wrapping>'''

        tr = testrunner.TestRunner( 'testpath', 1, self.logfolder )
        tr.shutdown = Mock()
        tr.parse( etree.fromstring( testsuite ) )
        self.assertEqual( 1, tr.shutdown.call_count )

    def test_parser_shutdown_is_called_if_node_function_raises( self ):
        """ test whether shutdown is called if a node fuinction raises
        """
        testsuite = '''<wrapping name="facet genreCategory">
                        <setup xmlns="info:testsuite#"
                               xmlns:s="http://dbc.dk/xml/namespaces/solr">
                        </setup>
                        <test xmlns="info:testsuite#"
                              xmlns:s="http://dbc.dk/xml/namespaces/solr"
                              name="facet genreCategory">
                         <s:myfunc/>
                        </test>
                       </wrapping>'''

        def myfunc( node ):
            raise RuntimeError( 'foo error' )

        tr = testrunner.TestRunner( 'testpath', 1, self.logfolder )
        tr.parser_functions.update( {'{http://dbc.dk/xml/namespaces/solr}myfunc': myfunc} )
        tr.shutdown = Mock()

        self.failUnlessRaises( RuntimeError, tr.parse, etree.fromstring( testsuite ) )
        self.assertEqual( 1, tr.shutdown.call_count )
