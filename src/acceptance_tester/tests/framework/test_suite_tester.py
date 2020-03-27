#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-

import datetime
import os
import pkg_resources
import unittest
import shutil
import tempfile
from mock import call
from mock import Mock
from mock import patch
import zipfile
from lxml import etree
import io

from acceptance_tester.framework.suite_tester import SuiteTester as SuiteTester
import acceptance_tester.framework.validate_testsuite as validate_testsuite
import acceptance_tester.framework.load_testrunner
import acceptance_tester.framework.suite_tester
import acceptance_tester.framework.rst_creator as rst_creator
import acceptance_tester.framework.job as job
import acceptance_tester.framework.find_tests as find_tests


example_xsd = '''<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                             targetNamespace="urn:books"
                             xmlns:bks="urn:books">

                  <xsd:element name="books" type="bks:BooksForm"/>

                  <xsd:complexType name="BooksForm">
                   <xsd:sequence>
                    <xsd:element name="book"
                                 type="bks:BookForm"
                                 minOccurs="0"
                                 maxOccurs="unbounded"/>
                   </xsd:sequence>
                  </xsd:complexType>
                  <xsd:complexType name="BookForm">
                   <xsd:sequence>
                    <xsd:element name="author"   type="xsd:string"/>
                    <xsd:element name="title"    type="xsd:string"/>
                    <xsd:element name="genre"    type="xsd:string"/>
                    <xsd:element name="price"    type="xsd:float" />
                    <xsd:element name="pub_date" type="xsd:date" />
                    <xsd:element name="review"   type="xsd:string"/>
                   </xsd:sequence>
                   <xsd:attribute name="id"   type="xsd:string"/>
                  </xsd:complexType>
                 </xsd:schema>'''

valid_xml = '''<?xml version="1.0"?>
                <x:books xmlns:x="urn:books">
                 <book id="bk001">
                  <author>Writer</author>
                  <title>The First Book</title>
                  <genre>Fiction</genre>
                  <price>44.95</price>
                  <pub_date>2000-10-01</pub_date>
                  <review>An amazing story of nothing.</review>
                 </book>

                 <book id="bk002">
                  <author>Poet</author>
                  <title>The Poets First Poem</title>
                  <genre>Poem</genre>
                  <price>24.95</price>
                  <pub_date>2000-10-01</pub_date>
                  <review>An amazing story of nothing.</review>
                 </book>
                </x:books>'''

non_valid_xml = '''<?xml version="1.0"?>
                <x:books xmlns:x="urn:books">
                 <foo id="bk001">
                  <author>Writer</author>
                  <title>The First Book</title>
                  <genre>Fiction</genre>
                  <price>44.95</price>
                  <pub_date>2000-10-01</pub_date>
                  <review>An amazing story of nothing.</review>
                 </foo>
                 <book id="bk002">
                  <author>Poet</author>
                  <title>The Poets First Poem</title>
                  <genre>Poem</genre>
                  <price>24.95</price>
                  <review>Least poetic poems.</review>
                 </book>
                </x:books>'''

testsuite1 = '''<?xml version="1.0" encoding="UTF-8"?>
                 <testsuite xmlns="info:testsuite#"
                            xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo"
                            xmlns:hv="http://dbc.dk/xml/namespaces/hive"
                            type="hive-fcrepo">
                  <setup>
                   <fc:fcrepo type="normal" />
                   <hv:hive type="normal">
                    <hv:properties>
                     <hv:property name="HarvestDir" value="../../es-files/new_record_error"/>
                    </hv:properties>
                   </hv:hive>
                  </setup>
                  <test name="test1">
                   <hv:run/>

                   <fc:search expected="4">
                    <fc:condition>
                     <fc:element value="pid"/>
                     <fc:operator value="="/>
                     <fc:value value="*"/>
                    </fc:condition>
                   </fc:search>
                  </test>
                 </testsuite>'''

testsuite2 = '''<?xml version="1.0" encoding="UTF-8"?>
                 <testsuite xmlns="info:testsuite#"
                            xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo"
                            xmlns:hv="http://dbc.dk/xml/namespaces/hive"
                            type="hive-fcrepo">
                  <setup>
                   <fc:fcrepo type="normal" />
                   <hv:hive type="normal">
                    <hv:properties>
                     <hv:property name="HarvestDir" value="../../es-files/new_record_error"/>
                    </hv:properties>
                   </hv:hive>
                  </setup>
                  <test name="test1">
                   <hv:run/>

                   <fc:search expected="4">
                    <fc:condition>
                     <fc:element value="pid"/>
                     <fc:operator value="="/>
                     <fc:value value="*"/>
                    </fc:condition>
                   </fc:search>
                  </test>
                 <test name="test2">
                   <hv:run/>

                   <fc:search expected="4">
                    <fc:condition>
                     <fc:element value="pid"/>
                     <fc:operator value="="/>
                     <fc:value value="*"/>
                    </fc:condition>
                   </fc:search>
                  </test>
                 </testsuite>'''


testsuite3 = '''<?xml version="1.0" encoding="UTF-8"?>
                 <testsuite xmlns="info:testsuite#"
                            xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo"
                            xmlns:ad="http://dbc.dk/xml/namespaces/addi"
                            type="addi-fcrepo">
                  <setup>
                   <fc:fcrepo type="normal" />
                   <ad:addiService/>
                  </setup>
                  <test name="book has adaptation movie">
                   <fc:ingest type="folder" value="../../../../fedora-test-objects/adaptation" expected="3"/>
                   <ad:addJob pid="unit:5"/>
                   <fc:checkAddi subject="unit:5" predicate="http://oss.dbc.dk/rdf/dbcaddi#hasAdaptation" object="unit:9"/>
                   <fc:checkAddi subject="unit:9" predicate="http://oss.dbc.dk/rdf/dbcaddi#isAdaptationOf" object="unit:5"/>
                   <fc:checkAddi subject="unit:5" predicate="http://oss.dbc.dk/rdf/dbcaddi#hasAdaptation" object="unit:8"/>
                   <fc:checkAddi subject="unit:18" predicate="http://oss.dbc.dk/rdf/dbcaddi#isAdaptationOf" object="unit:5"/>
                  </test>
                 </testsuite>'''


def normalize_xml( xml_or_string ):
    parser = etree.XMLParser( remove_blank_text=True, encoding="UTF-8" )


    xml = xml_or_string
    if type( xml_or_string ) == str:
        xml = etree.parse( io.StringIO( xml_or_string ), parser )

    return etree.tostring( xml, pretty_print=True, encoding="UTF-8" )


def parse_xUnit_result( xml ):
    root = xml.getroot()
    tests = root.get( "tests" )
    errors = root.get( "errors" )
    failures = root.get( "failures" )
    return { "tests": tests,
             'errors': errors,
             'failures': failures }


class TestSuiteTester( unittest.TestCase ):

    def setUp( self ):
        self.test_folder = tempfile.mkdtemp()
        self.org_init = SuiteTester.__init__

        self.arguments = [ ['path/to/tests'],
                           os.path.join( self.test_folder, 'build-folder' ),
                           os.path.join( self.test_folder, 'resource-folder' ),
                           os.path.join( self.test_folder, 'test-report-folder' ),
                           os.path.join( self.test_folder, 'report-file' ),
                           os.path.join( self.test_folder, 'log-file' ),
                           "testrunner-config",
                           '1',
                           False,
                           None,
                           True ]

    def tearDown( self ):
        SuiteTester.__init__ = self.org_init
        shutil.rmtree( self.test_folder )

    def test_suitetester_raises_if_pool_size_is_less_than_one( self ):
        """ Test whether the suitetester constructor raises if pool size < 1
        """
        arguments = self.arguments
        arguments[6] = 0
        self.assertRaises( RuntimeError, SuiteTester, *arguments )

    def test_suitetester_raises_if_port_range_list_is_bigger_than_2( self ):
        """ Tests whether a runtime error is raised if the port range list is bigger than 2
        """
        arguments = self.arguments
        self.assertRaises( RuntimeError, SuiteTester, *arguments, port_range="1000-2000-3000" )

    def test_suitetester_raises_if_1_element_of_port_range_is_bigger_than_the_2_element( self ):
        """ Test whether the suitetest constructor raises if the 1. element of port range is bigger than the 2. element.
        """
        arguments = self.arguments
        self.assertRaises( RuntimeError, SuiteTester, *arguments, port_range="3000-2000" )

    def test_suite_tester_raises_if_testrunner_is_not_present( self ):
        """ Test whether a runtime error is raised if testrunner is not present for test type
        """

        acceptance_tester.framework.find_tests._find_testsuites = Mock( return_value=['foo'] )
        acceptance_tester.framework.find_tests._get_test_type = Mock( return_value=( 'unknown-type', {'resource-manager': None } ) )
        self.assertRaises( RuntimeError, acceptance_tester.framework.suite_tester.SuiteTester, *self.arguments )

    def test_suite_parser_test_suites_are_filtered_according_to_xsd_if_provided( self ):
        """ Test whether the _filter_non_valid_testsuites is called if xsd is provided
        """
        acceptance_tester.framework.find_tests._find_testsuites = Mock( return_value=['foo'] )
        acceptance_tester.framework.find_tests._get_test_type = Mock( return_value=( 'unknown-type', {'test-runner': None, 'resource-manager': None, 'xsd': 'bar' } ) )

        acceptance_tester.framework.find_tests._get_tests = Mock( return_value=[] )
        acceptance_tester.framework.find_tests._filter_non_valid_suites = Mock( return_value=[] )

        acceptance_tester.framework.suite_tester.SuiteTester( *self.arguments )

        expected = call(['foo'], {'test-runner': None, 'xsd': 'bar', 'resource-manager': None})
        self.assertEqual( expected, acceptance_tester.framework.find_tests._filter_non_valid_suites.call_args )

    # def test_suite_parser_test_arguments_looks_as_expected( self ):
    #     """ Test whether the test arguments build by the constructor looks as expected
    #     """

    #     retrieved_tests = [('/home/shm/repos/svn.dbc.dk/repos/fcrepo-solr-acctest/trunk/testsuites/verified/facet-genrecategory.xml', 'facet genreCategory', '<wrapping name="facet genreCategory"><setup xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:s="http://dbc.dk/xml/namespaces/solr">\n  <fc:fcrepo type="normal"/>\n  <s:solr type="normal"/>\n</setup>\n<test xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:s="http://dbc.dk/xml/namespaces/solr" name="facet genreCategory">\n  <description>facet.genreCategory</description>\n  <fc:ingest type="file" value="../../fedora-test-objects/facet-genrecategory/870970-basis_23645564.xml"/>\n  <s:batchimport>\n    <s:from value="now" delta="-3h"/>\n    <s:until value="now"/>\n  </s:batchimport>\n  <s:search string="facet.genreCategory:fiktion" expected="1">\n    <s:id value="870970-basis:23645564"/>\n  </s:search>\n  <s:search string="facet.genreCategory:mus" expected="0"/>\n</test>\n</wrapping>', {'description': 'facet.genreCategory'})]

    #     acceptance_tester.framework.find_tests._find_testsuites = Mock( return_value=['foo'] )
    #     acceptance_tester.framework.find_tests._get_test_type = Mock( return_value=( 'unknown-type', {'test-runner': None, 'resource-manager': None } ) )

    #     acceptance_tester.framework.find_tests._get_tests = Mock( return_value=retrieved_tests )

    #     st = acceptance_tester.framework.suite_tester.SuiteTester( *self.arguments )

    #     expected_keys = [ 'build-folder', 'log-folder', 'name', 'documentation', 'id', 'report-file', 'test-suite', 'type', 'type-name', 'verbose', 'xml', 'color' ]
    #     for key in expected_keys:
    #         self.assertTrue( key in st.tests[0] )

    #     self.assertEqual( 0, st.tests[0]['id'] )
    #     self.assertEqual( 'facet genreCategory', st.tests[0]['name'] )
    #     self.assertEqual( 'unknown-type', st.tests[0]['type-name'] )

    # @patch( 'multiprocessing.Pool' )
    # def test_run_returns_without_starting_anything_if_no_tests_are_present( self, mock_cls ):
    #     """ Test that the run method does not start a pool if no tests are present
    #     """
    #     st = acceptance_tester.framework.suite_tester.SuiteTester( *self.arguments )

    #     st.test_type = ['foo']
    #     st.tests = [{}]
    #     log_folder = os.path.join( self.test_folder, 'log-folder' )
    #     os.mkdir( log_folder )
    #     st.log_folder = log_folder

    #     test_results_folder = os.path.join( self.test_folder, 'test-report-folder' )
    #     os.mkdir( test_results_folder )
    #     st.test_results_folder = test_results_folder

    #     st.delimiter_length = 120
    #     st.number_of_tests = 1
    #     st.number_of_testsuites = 1

    #     rst_creator.create_test_documentation = Mock( retrun_value=None )

    #     tmock = Mock()
    #     tmock.map.return_value=[]
    #     tmock.close.return_value=None
    #     tmock.join.return_value=None

    #     mock_cls.return_value=tmock

    #     st.test_type = None
    #     # When
    #     st.run()

    #     # Then
    #     self.assertEqual( 0, tmock.close.call_count )
    #     self.assertEqual( 0, tmock.join.call_count )
    #     self.assertEqual( 0, tmock.map.call_count )

    # @patch( 'multiprocessing.Pool' )
    # def test_run_pool_is_called_with_expected_arguments( self, mock_cls):
    #     """ Test that the run method creates and calls the pool with expected arguments
    #     """
    #     # Given
    #     st = acceptance_tester.framework.suite_tester.SuiteTester( *self.arguments, color=True )

    #     st.test_type = ['foo']
    #     st.tests = [{}]
    #     log_folder = os.path.join( self.test_folder, 'log-folder' )
    #     os.mkdir( log_folder )
    #     st.log_folder = log_folder

    #     test_results_folder = os.path.join( self.test_folder, 'test-report-folder' )
    #     os.mkdir( test_results_folder )
    #     st.test_results_folder = test_results_folder

    #     st.delimiter_length = 120
    #     st.number_of_tests = 1
    #     st.number_of_testsuites = 1

    #     rst_creator.create_test_documentation = Mock( retrun_value=None )

    #     tmock = Mock()
    #     tmock.map.return_value=[]
    #     tmock.close.return_value=None
    #     tmock.join.return_value=None

    #     mock_cls.return_value=tmock

    #     # When
    #     st.run()

    #     # Then
    #     self.assertEqual( 1, tmock.close.call_count )
    #     self.assertEqual( 1, tmock.join.call_count )

    #     expected = call( job.job, [{'resource-manager': None}] )

    #     self.assertEqual( expected, tmock.map.call_args )

    # def test_create_folder_returns_absolute_file_path( self ):
    #     """ Test whether the _create_folder returns the absolute path
    #     """
    #     SuiteTester.__init__ = lambda x: None

    #     cwd = os.getcwd()
    #     os.chdir( self.test_folder )

    #     st = SuiteTester()
    #     expected = os.path.join( self.test_folder, "foo-folder" )
    #     result = st._create_folder( "foo-folder" )

    #     self.assertEqual( expected, result )

    #     os.chdir( cwd )

    # def test_create_folder_creates_expected_folder( self ):
    #     """ Test whether the _create_folder creates folder as expected
    #     """
    #     SuiteTester.__init__ = lambda x: None

    #     cwd = os.getcwd()
    #     os.chdir( self.test_folder )

    #     st = SuiteTester()
    #     st._create_folder( "foo-folder" )

    #     expected = os.path.join( self.test_folder, "foo-folder" )
    #     self.assertTrue( os.path.exists( expected ) )

    #     os.chdir( cwd )

    # def test_create_folder_returns_expected_path_if_folder_exists( self ):
    #     """ Test whether the _create_folder method returns the expected path if folder already exists.
    #     """
    #     SuiteTester.__init__ = lambda x: None
    #     expected = os.path.join( self.test_folder, "foo-folder" )
    #     os.mkdir( expected )

    #     cwd = os.getcwd()
    #     os.chdir( self.test_folder )

    #     st = SuiteTester()
    #     result = st._create_folder( "foo-folder" )

    #     self.assertEqual( expected, result )

    #     os.chdir( cwd )

    # def test_create_folder_name_returns_the_expected_name_based_on_the_arguments( self ):
    #     """ Test that _create_folder_name returns the expected name based on the arguments
    #     """
    #     SuiteTester.__init__ = lambda x: None

    #     st = SuiteTester()
    #     st.build_folder = 'test-build-folder'
    #     result = st._create_folder_name( "suite-file", "bar test name" )
    #     expected = 'test-build-folder/suite-fil___bar_test_name'
    #     self.assertEqual( expected, result )

    # def test_zip_logs_all_files_present_in_zip_file( self ):
    #     """ Test that zip_logs zips all files as expected
    #     """

    #     log_folder = os.path.join( self.test_folder, 'log-folder' )
    #     log_file = os.path.join( self.test_folder, 'zipfile.zip')
    #     os.mkdir( log_folder )

    #     ex_files = []
    #     for i in range( 1, 4 ):
    #         name = "example_file_%s"%i
    #         path = os.path.join( log_folder, name )
    #         fh = open( path, 'w' )
    #         fh.write( "foo" )
    #         fh.close()
    #         ex_files.append( name )

    #     SuiteTester.__init__ = lambda x: None
    #     st = SuiteTester()
    #     st.log_file = log_file
    #     st.log_folder = log_folder


    #     st._zip_logs()

    #     self.assertTrue( os.path.exists( log_file ) )
    #     zfile = zipfile.ZipFile( log_file )
    #     names = zfile.namelist()
    #     for ef in ex_files:
    #         present = False
    #         for name in names:
    #             if ef in name:
    #                 present = True
    #                 break
    #         self.assertTrue( present )

    #     zfile.close()

    # def test_filter_non_valid_suites_non_valid_files_are_filtered_out( self ):
    #     """ Test whether _filter_non_valid_suites filters non-valid suite files.
    #     """
    #     schema = etree.XMLSchema( etree.fromstring( example_xsd ) )

    #     find_tests._get_schema = Mock( return_value=schema )

    #     suites = [ ( 'valid-test', etree.fromstring( valid_xml ) ),
    #                ( 'non_valid-test', etree.fromstring( non_valid_xml ) ) ]

    #     result = find_tests._filter_non_valid_suites( suites, {'xsd' : 'type' } )

    #     self.assertEqual( 1, len( result ) )
    #     self.assertEqual( 'valid-test', result[0][0] )

    # def test_filter_non_valid_suites_error_is_raised_if_no_valid_suites_are_found( self ):
    #     """ Test whether a runtimeerror is raised if no valid testsuites are found
    #     """
    #     schema = etree.XMLSchema( etree.fromstring( example_xsd ) )

    #     find_tests._get_schema = Mock( return_value=schema )

    #     suites = [ ( 'non_valid-test', etree.fromstring( non_valid_xml ) ) ]

    #     self.failUnlessRaises( RuntimeError, find_tests._filter_non_valid_suites, suites, {'xsd' : 'type' } )

    # def test_find_testsuites_only_xml_files_are_examined( self ):
    #     """ Test that only xml files are registered as testsuites
    #     """
    #     ex_files = []
    #     for i in range( 1, 4 ):
    #         name = "example_xml_%s.xml"%i
    #         path = os.path.join( self.test_folder, name )
    #         fh = open( path, 'w' )
    #         fh.write( "foo" )
    #         fh.close()
    #         ex_files.append( name )

    #     not_xml_file = os.path.join( self.test_folder, 'noxml.txt' )
    #     fh = open( not_xml_file, 'w' )
    #     fh.write( "foo" )
    #     fh.close()

    #     org_vdf = validate_testsuite.validate_testsuite_file
    #     validate_testsuite.validate_testsuite_file = Mock( return_value='example xml' )

    #     result = find_tests._find_testsuites( self.test_folder )

    #     sorted_result = map( lambda x: os.path.basename( x[0] ), result )
    #     sorted_result.sort()

    #     self.assertEqual( ex_files, sorted_result )
    #     self.assertFalse( not_xml_file in sorted_result )

    #     validate_testsuite.validate_testsuite_file = org_vdf

    # def test_get_test_type_returns_expected_( self ):
    #     """ Test that get_test_type returns the expected testtype
    #     """
    #     parser = etree.XMLParser( remove_blank_text=True, encoding="UTF-8" )
    #     xml1 = etree.parse( StringIO.StringIO( testsuite1 ), parser )

    #     acceptance_tester.framework.load_testrunner.load_testrunner = Mock( return_value=None )

    #     result = find_tests._get_test_type( [xml1] )

    #     self.assertEqual( 'hive-fcrepo', result[0] )

    # def test_get_test_type_raises_error_if_multiple_test_types_are_present( self ):
    #     """ Test that get_test_type raises a runtimeerror if multiple test types are present
    #     """
    #     parser = etree.XMLParser( remove_blank_text=True, encoding="UTF-8" )
    #     xml1 = etree.parse( StringIO.StringIO( testsuite1 ), parser )
    #     xml2 = etree.parse( StringIO.StringIO( testsuite3 ), parser )

    #     acceptance_tester.framework.load_testrunner.load_testrunner = Mock( return_value=None )

    #     self.failUnlessRaises( RuntimeError, find_tests._get_test_type, [xml1, xml2] )

    # def test_get_tests_wrap_setup_node_and_test_node_as_expected( self ):
    #     """ Test whether the get_tests method wraps up a setup and test node as expected
    #     """
    #     parser = etree.XMLParser( remove_blank_text=True, encoding="UTF-8" )
    #     xml = etree.parse( StringIO.StringIO( testsuite1 ), parser )
    #     suites = [ ( None, xml ) ]

    #     result = find_tests._get_tests( suites )

    #     expected = '''<wrapping name="test1">
    #                    <setup xmlns="info:testsuite#"
    #                           xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo"
    #                           xmlns:hv="http://dbc.dk/xml/namespaces/hive">
    #                     <fc:fcrepo type="normal"/>
    #                      <hv:hive type="normal">
    #                       <hv:properties>
    #                        <hv:property name="HarvestDir" value="../../es-files/new_record_error"/>
    #                       </hv:properties>
    #                      </hv:hive>
    #                     </setup>
    #                     <test xmlns="info:testsuite#"
    #                           xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo"
    #                           xmlns:hv="http://dbc.dk/xml/namespaces/hive"
    #                           name="test1">
    #                      <hv:run/>
    #                       <fc:search expected="4">
    #                        <fc:condition>
    #                         <fc:element value="pid"/>
    #                         <fc:operator value="="/>
    #                         <fc:value value="*"/>
    #                        </fc:condition>
    #                       </fc:search>
    #                      </test>
    #                     </wrapping>'''

    #     self.assertEqual( 1, len( result ) )
    #     self.assertEqual( normalize_xml( expected ), normalize_xml( result[0][2] ) )

    # def test_get_tests_multiple_test_nodes_share_same_setup_node( self ):
    #     """ Test whether the get_tests method wraps up multiple test nodes with the same setup node
    #     """
    #     parser = etree.XMLParser( remove_blank_text=True, encoding="UTF-8" )
    #     xml = etree.parse( StringIO.StringIO( testsuite2 ), parser )
    #     suites = [ ( None, xml ) ]

    #     result = find_tests._get_tests( suites )

    #     expected1 = '''<wrapping name="test1">
    #                     <setup xmlns="info:testsuite#"
    #                            xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo"
    #                            xmlns:hv="http://dbc.dk/xml/namespaces/hive">
    #                      <fc:fcrepo type="normal"/>
    #                       <hv:hive type="normal">
    #                        <hv:properties>
    #                         <hv:property name="HarvestDir" value="../../es-files/new_record_error"/>
    #                        </hv:properties>
    #                       </hv:hive>
    #                      </setup>
    #                      <test xmlns="info:testsuite#"
    #                            xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo"
    #                            xmlns:hv="http://dbc.dk/xml/namespaces/hive"
    #                            name="test1">
    #                       <hv:run/>
    #                        <fc:search expected="4">
    #                         <fc:condition>
    #                          <fc:element value="pid"/>
    #                          <fc:operator value="="/>
    #                          <fc:value value="*"/>
    #                         </fc:condition>
    #                        </fc:search>
    #                       </test>
    #                      </wrapping>'''

    #     expected2 = '''<wrapping name="test2">
    #                     <setup xmlns="info:testsuite#"
    #                            xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo"
    #                            xmlns:hv="http://dbc.dk/xml/namespaces/hive">
    #                      <fc:fcrepo type="normal"/>
    #                       <hv:hive type="normal">
    #                        <hv:properties>
    #                         <hv:property name="HarvestDir" value="../../es-files/new_record_error"/>
    #                        </hv:properties>
    #                       </hv:hive>
    #                      </setup>
    #                      <test xmlns="info:testsuite#"
    #                            xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo"
    #                            xmlns:hv="http://dbc.dk/xml/namespaces/hive"
    #                            name="test2">
    #                       <hv:run/>
    #                        <fc:search expected="4">
    #                         <fc:condition>
    #                          <fc:element value="pid"/>
    #                          <fc:operator value="="/>
    #                          <fc:value value="*"/>
    #                         </fc:condition>
    #                        </fc:search>
    #                       </test>
    #                      </wrapping>'''

    #     self.assertEqual( 2, len( result ) )
    #     self.assertEqual( normalize_xml( expected1 ), normalize_xml( result[0][2] ) )
    #     self.assertEqual( normalize_xml( expected2 ), normalize_xml( result[1][2] ) )

    # def test_get_tests_titles_banned_chars_raises_a_runtimeerror( self ):
    #     """ Test whether a title with a banned character raises a a runtimeerror as expected
    #     """
    #     banned = '''<?xml version="1.0" encoding="UTF-8"?>
    #              <testsuite xmlns="info:testsuite#"
    #                         xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo"
    #                         xmlns:hv="http://dbc.dk/xml/namespaces/hive"
    #                         type="hive-fcrepo">
    #               <setup>
    #                <fc:fcrepo type="normal" />
    #                <hv:hive type="normal">
    #                 <hv:properties>
    #                  <hv:property name="HarvestDir" value="../../es-files/new_record_error"/>
    #                 </hv:properties>
    #                </hv:hive>
    #               </setup>
    #               <test name="Title with Banned Char (For Real !)">
    #                <hv:run/>
    #                <fc:search expected="4">
    #                 <fc:condition>
    #                  <fc:element value="pid"/>
    #                  <fc:operator value="="/>
    #                  <fc:value value="*"/>
    #                 </fc:condition>
    #                </fc:search>
    #               </test>
    #              </testsuite>'''

    #     parser = etree.XMLParser( remove_blank_text=True, encoding="UTF-8" )
    #     xml = etree.parse( StringIO.StringIO( banned ), parser )
    #     suites = [ ( None, xml ) ]

    #     self.failUnlessRaises( RuntimeError, find_tests._get_tests, suites )

    # def test_get_tests_raises_no_actual_tests_where_found_during_search( self ):
    #     """ Test whether the method raises a runtimeerror if no tests are found during search
    #     """

    #     suites = []
    #     self.failUnlessRaises( RuntimeError, find_tests._get_tests, suites )

    # def test_write_junit_files_writes_expected_files( self ):
    #     """ Test wether the expected xUnit files are written
    #     """
    #     SuiteTester.__init__ = lambda x: None
    #     st = SuiteTester()
    #     st.test_results_folder = self.test_folder

    #     testresult = [{'status': 'SUCCESS', 'xml': '<wrapping name="facet genreCategory">\n  <setup xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:s="http://dbc.dk/xml/namespaces/solr">\n    <fc:fcrepo type="normal"/>\n    <s:solr type="normal"/>\n  </setup>\n  <test xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:s="http://dbc.dk/xml/namespaces/solr" name="facet genreCategory">\n    <description>facet.genreCategory</description>\n    <fc:ingest type="file" value="../../fedora-test-objects/facet-genrecategory/870970-basis_23645564.xml"/>\n    <s:batchimport>\n      <s:from value="now" delta="-3h"/>\n      <s:until value="now"/>\n    </s:batchimport>\n    <s:search string="facet.genreCategory:fiktion" expected="1">\n      <s:id value="870970-basis:23645564"/>\n    </s:search>\n    <s:search string="facet.genreCategory:mus" expected="0"/>\n  </test>\n</wrapping>\n', 'errors': [], 'status-msg': "Test 'facet genreCategory' status: SUCCESS.", 'test-suite': '/home/shm/repos/svn.dbc.dk/repos/fcrepo-solr-acctest/trunk/testsuites/verified/facet-genrecategory.xml', 'documentation': {'description': 'facet.genreCategory'}, 'type-name': 'fcrepo-solr', 'summary': ['------------------------------------------------------------------------------------------------------------------------', 'Test Summary:', "  testfile: '/home/shm/repos/svn.dbc.dk/repos/fcrepo-solr-acctest/trunk/testsuites/verified/facet-genrecategory.xml'", "  testname: 'facet genreCategory'", '  status: \x1b[32m\x1b[1mSUCCESS\x1b[39m\x1b[0m', '  duration: 36 seconds', '------------------------------------------------------------------------------------------------------------------------'], 'time': datetime.timedelta(0, 36, 868673), 'failures': [], 'build-folder': '/home/shm/repos/svn.dbc.dk/repos/acceptance-tester-dev/trunk/build-folder/facet-genrecategory___facet_genreCategory_2', 'name': 'facet genreCategory'}]

    #     st._write_junit_files( testresult )
    #     expected_file = os.path.join( self.test_folder, 'xUnit',
    #                                   'TEST-home.shm.repos.svn.dbc.dk.repos.fcrepo-solr-acctest.trunk.testsuites.verified.facet-genrecategory.xml' )

    #     self.assertTrue( os.path.exists( os.path.join( self.test_folder, 'xUnit' ) ) )
    #     self.assertTrue( os.path.exists( expected_file ) )

    # def test_write_junit_test_successfull_test( self ):
    #     """ Test whether a write_junit creates the expected report file with a successfull test
    #     """
    #     SuiteTester.__init__ = lambda x: None
    #     st = SuiteTester()
    #     st.test_results_folder = self.test_folder

    #     testresult = [{'status': 'SUCCESS', 'xml': '<wrapping name="facet genreCategory">\n  <setup xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:s="http://dbc.dk/xml/namespaces/solr">\n    <fc:fcrepo type="normal"/>\n    <s:solr type="normal"/>\n  </setup>\n  <test xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:s="http://dbc.dk/xml/namespaces/solr" name="facet genreCategory">\n    <description>facet.genreCategory</description>\n    <fc:ingest type="file" value="../../fedora-test-objects/facet-genrecategory/870970-basis_23645564.xml"/>\n    <s:batchimport>\n      <s:from value="now" delta="-3h"/>\n      <s:until value="now"/>\n    </s:batchimport>\n    <s:search string="facet.genreCategory:fiktion" expected="1">\n      <s:id value="870970-basis:23645564"/>\n    </s:search>\n    <s:search string="facet.genreCategory:mus" expected="0"/>\n  </test>\n</wrapping>\n', 'errors': [], 'status-msg': "Test 'facet genreCategory' status: SUCCESS.", 'test-suite': '/home/shm/repos/svn.dbc.dk/repos/fcrepo-solr-acctest/trunk/testsuites/verified/facet-genrecategory.xml', 'documentation': {'description': 'facet.genreCategory'}, 'type-name': 'fcrepo-solr', 'summary': ['------------------------------------------------------------------------------------------------------------------------', 'Test Summary:', "  testfile: '/home/shm/repos/svn.dbc.dk/repos/fcrepo-solr-acctest/trunk/testsuites/verified/facet-genrecategory.xml'", "  testname: 'facet genreCategory'", '  status: \x1b[32m\x1b[1mSUCCESS\x1b[39m\x1b[0m', '  duration: 36 seconds', '------------------------------------------------------------------------------------------------------------------------'], 'time': datetime.timedelta(0, 36, 868673), 'failures': [], 'build-folder': '/home/shm/repos/svn.dbc.dk/repos/acceptance-tester-dev/trunk/build-folder/facet-genrecategory___facet_genreCategory_2', 'name': 'facet genreCategory'}]

    #     st._write_junit_files( testresult )

    #     parser = etree.XMLParser( remove_blank_text=True, encoding="UTF-8" )
    #     xml = etree.parse( os.path.join( self.test_folder, 'xUnit', 'TEST-home.shm.repos.svn.dbc.dk.repos.fcrepo-solr-acctest.trunk.testsuites.verified.facet-genrecategory.xml' ),
    #                        parser )

    #     result = parse_xUnit_result( xml )
    #     self.assertEqual( 1, int( result['tests'] ) )
    #     self.assertEqual( 0, int( result['errors'] ) )
    #     self.assertEqual( 0, int( result['failures'] ) )

    # def test_write_junit_test_failed_test( self ):
    #     """ Test whether a write_junit creates the expected report file with a failed test
    #     """
    #     SuiteTester.__init__ = lambda x: None
    #     st = SuiteTester()
    #     st.test_results_folder = self.test_folder

    #     testresult = [{'status': 'FAILURE', 'xml': '<wrapping name="facet genreCategory">\n  <setup xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:s="http://dbc.dk/xml/namespaces/solr">\n    <fc:fcrepo type="normal"/>\n    <s:solr type="normal"/>\n  </setup>\n  <test xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:s="http://dbc.dk/xml/namespaces/solr" name="facet genreCategory">\n    <description>facet.genreCategory</description>\n    <fc:ingest type="file" value="../../fedora-test-objects/facet-genrecategory/870970-basis_23645564.xml"/>\n    <s:batchimport>\n      <s:from value="now" delta="-3h"/>\n      <s:until value="now"/>\n    </s:batchimport>\n    <s:search string="facet.genreCategory:fiktion" expected="1">\n      <s:id value="870970-basis:23645564"/>\n    </s:search>\n    <s:search string="facet.genreCategory:mus" expected="10"/>\n  </test>\n</wrapping>\n', 'errors': [], 'status-msg': "Test 'facet genreCategory' status: FAILED.", 'test-suite': '/home/shm/repos/svn.dbc.dk/repos/fcrepo-solr-acctest/trunk/testsuites/verified/facet-genrecategory.xml', 'documentation': {'description': 'facet.genreCategory'}, 'type-name': 'fcrepo-solr', 'summary': ['------------------------------------------------------------------------------------------------------------------------', 'Test Summary:', "  testfile: '/home/shm/repos/svn.dbc.dk/repos/fcrepo-solr-acctest/trunk/testsuites/verified/facet-genrecategory.xml'", "  testname: 'facet genreCategory'", '  status: \x1b[33m\x1b[1mFAILED\x1b[39m\x1b[0m', '', 'expected 10 records found, got 0.', '', '  duration: 45 seconds', '------------------------------------------------------------------------------------------------------------------------'], 'time': datetime.timedelta(0, 45, 424306), 'failures': ['expected 10 records found, got 0.'], 'build-folder': '/home/shm/repos/svn.dbc.dk/repos/acceptance-tester-dev/trunk/build-folder/facet-genrecategory___facet_genreCategory_2', 'name': 'facet genreCategory'}]

    #     st._write_junit_files( testresult )

    #     parser = etree.XMLParser( remove_blank_text=True, encoding="UTF-8" )
    #     xml = etree.parse( os.path.join( self.test_folder, 'xUnit', 'TEST-home.shm.repos.svn.dbc.dk.repos.fcrepo-solr-acctest.trunk.testsuites.verified.facet-genrecategory.xml' ),
    #                        parser )

    #     result = parse_xUnit_result( xml )
    #     self.assertEqual( 1, int( result['tests'] ) )
    #     self.assertEqual( 0, int( result['errors'] ) )
    #     self.assertEqual( 1, int( result['failures'] ) )

    # def test_write_junit_test_error_test( self ):
    #     """ Test whether a write_junit creates the expected report file with a test that raise an error
    #     """
    #     SuiteTester.__init__ = lambda x: None
    #     st = SuiteTester()
    #     st.test_results_folder = self.test_folder

    #     testresult = [{'status': 'ERROR', 'xml': '<wrapping name="facet genreCategory">\n  <setup xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:s="http://dbc.dk/xml/namespaces/solr">\n    <s:solr type="normal"/>\n  </setup>\n  <test xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:s="http://dbc.dk/xml/namespaces/solr" name="facet genreCategory">\n    <description>facet.genreCategory</description>\n    <fc:ingest type="file" value="../../fedora-test-objects/facet-genrecategory/870970-basis_23645564.xml"/>\n    <s:search string="facet.genreCategory:fiktion" expected="1">\n      <s:id value="870970-basis:23645564"/>\n    </s:search>\n    <s:search string="facet.genreCategory:mus" expected="0"/>\n  </test>\n</wrapping>\n', 'errors': ['Traceback (most recent call last):\n  File "/home/shm/repos/svn.dbc.dk/repos/acceptance-tester-dev/trunk/externals/acceptance_tester/acceptance_tester/framework/job.py", line 363, in job\n    test[\'resource-manager\']  )\n  File "/home/shm/repos/svn.dbc.dk/repos/acceptance-tester-dev/trunk/externals/fcrepo_solr_testrunner/fcrepo_solr_testrunner/testrunner.py", line 93, in run_test\n    self.parse( test_xml )\n  File "/home/shm/repos/svn.dbc.dk/repos/acceptance-tester-dev/trunk/externals/acceptance_tester/acceptance_tester/abstract_testsuite_runner/test_runner.py", line 192, in parse\n    self.__update_out( *self.parser_functions[node.tag]( node ) )\n  File "/home/shm/repos/svn.dbc.dk/repos/acceptance-tester-dev/trunk/externals/os_python/os_python/fcrepo/fcrepo_parser.py", line 294, in ingest\n    ingested = self.repo.ingest( abspath )\n  File "/home/shm/repos/svn.dbc.dk/repos/acceptance-tester-dev/trunk/externals/os_python/os_python/fcrepo/fcrepo.py", line 368, in ingest\n    raise RuntimeError( err_str )\nRuntimeError: Ingest caused ERROR:\nError  : Connection refused\n'], 'status-msg': "Test 'facet genreCategory' status: ERROR.", 'test-suite': '/home/shm/repos/svn.dbc.dk/repos/fcrepo-solr-acctest/trunk/testsuites/verified/facet-genrecategory.xml', 'documentation': {'description': 'facet.genreCategory'}, 'type-name': 'fcrepo-solr', 'summary': ['------------------------------------------------------------------------------------------------------------------------', 'Test Summary:', "  testfile: '/home/shm/repos/svn.dbc.dk/repos/fcrepo-solr-acctest/trunk/testsuites/verified/facet-genrecategory.xml'", "  testname: 'facet genreCategory'", '  status: \x1b[31m\x1b[1mERROR\x1b[39m\x1b[0m', '', 'Traceback (most recent call last):\n  File "/home/shm/repos/svn.dbc.dk/repos/acceptance-tester-dev/trunk/externals/acceptance_tester/acceptance_tester/framework/job.py", line 363, in job\n    test[\'resource-manager\']  )\n  File "/home/shm/repos/svn.dbc.dk/repos/acceptance-tester-dev/trunk/externals/fcrepo_solr_testrunner/fcrepo_solr_testrunner/testrunner.py", line 93, in run_test\n    self.parse( test_xml )\n  File "/home/shm/repos/svn.dbc.dk/repos/acceptance-tester-dev/trunk/externals/acceptance_tester/acceptance_tester/abstract_testsuite_runner/test_runner.py", line 192, in parse\n    self.__update_out( *self.parser_functions[node.tag]( node ) )\n  File "/home/shm/repos/svn.dbc.dk/repos/acceptance-tester-dev/trunk/externals/os_python/os_python/fcrepo/fcrepo_parser.py", line 294, in ingest\n    ingested = self.repo.ingest( abspath )\n  File "/home/shm/repos/svn.dbc.dk/repos/acceptance-tester-dev/trunk/externals/os_python/os_python/fcrepo/fcrepo.py", line 368, in ingest\n    raise RuntimeError( err_str )\nRuntimeError: Ingest caused \x1b[31m\x1b[1mERROR\x1b[39m\x1b[0m:\nError  : Connection refused\n', '', '  duration: 14 seconds', '------------------------------------------------------------------------------------------------------------------------'], 'time': datetime.timedelta(0, 14, 163976), 'failures': [], 'build-folder': '/home/shm/repos/svn.dbc.dk/repos/acceptance-tester-dev/trunk/build-folder/facet-genrecategory___facet_genreCategory_2', 'name': 'facet genreCategory'}]

    #     st._write_junit_files( testresult )

    #     parser = etree.XMLParser( remove_blank_text=True, encoding="UTF-8" )
    #     xml = etree.parse( os.path.join( self.test_folder, 'xUnit', 'TEST-home.shm.repos.svn.dbc.dk.repos.fcrepo-solr-acctest.trunk.testsuites.verified.facet-genrecategory.xml' ),
    #                        parser )

    #     result = parse_xUnit_result( xml )
    #     self.assertEqual( 1, int( result['tests'] ) )
    #     self.assertEqual( 1, int( result['errors'] ) )
    #     self.assertEqual( 0, int( result['failures'] ) )

    # def test_write_lines_can_handle_string( self ):
    #     """ test whether write_lines can accept a string as argument as expected
    #     """
    #     SuiteTester.__init__ = lambda x: None
    #     st = SuiteTester()
    #     st.test_results_folder = self.test_folder
    #     report_file = os.path.join( self.test_folder, 'report-file' )
    #     st.report_file = report_file
    #     st.verbose = False
    #     st._write_lines( "test-line" )
    #     self.assertTrue( os.path.exists( report_file ) )
    #     fh = open( report_file )
    #     result = fh.read()
    #     fh.close()
    #     self.assertEqual( "test-line", result.strip() )

    # def test_write_lines_can_handle_list( self ):
    #     """ test whether write_lines can accept a list as argument as expected
    #     """
    #     SuiteTester.__init__ = lambda x: None
    #     st = SuiteTester()
    #     st.test_results_folder = self.test_folder
    #     report_file = os.path.join( self.test_folder, 'report-file' )
    #     st.report_file = report_file
    #     st.verbose = False
    #     st._write_lines( ["test-line 1", "test-line 2"] )
    #     self.assertTrue( os.path.exists( report_file ) )
    #     fh = open( report_file )
    #     result = fh.read()
    #     fh.close()
    #     self.assertEqual( "test-line 1\ntest-line 2", result.strip() )
