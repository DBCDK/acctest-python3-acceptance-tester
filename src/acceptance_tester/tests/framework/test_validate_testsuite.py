#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-

#import datetime
import os.path
import shutil
import StringIO
import sys
import tempfile
import unittest
from lxml import etree
from nose.tools import nottest


sys.path.insert( 0, os.path.dirname( os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( sys.argv[0] ) ) ) ) ) )
import acceptance_tester.framework.validate_testsuite as vt


class Test_validate_testsuite( unittest.TestCase ):

    def setUp( self ):
        self.test_folder = tempfile.mkdtemp()
        self.counter = 1

    def tearDown( self ):
        shutil.rmtree( self.test_folder )

    @nottest
    def write_test_file( self, string ):
        path = os.path.join( self.test_folder, "testfile%s"%self.counter  )
        self.counter += 1
        fh = open( path, 'w' )
        fh.write( string )
        fh.close()
        return path

    def test_non_xml_file_returns_none( self ):
        """
        tests whether 'None' is returned if input file isn't a xml file.
        """
        fname = self.write_test_file( 'meat' )
        rvalue = vt.validate_testsuite_file( fname )
        self.assertEqual( None, rvalue )

    def test_non_valid_xml_file_returns_none( self ):
        """
        tests whether 'None' is returned if input file is a non-valid xml file.
        """
        fname = self.write_test_file( '<schema></old>' )
        rvalue = vt.validate_testsuite_file( fname )
        self.assertEqual( None, rvalue )

    def test_wrong_namespace_retuens_none( self ):
        """
        Tests whether wrong namespace in input file returns 'None'.
        """
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
                 <testsuite xmlns="info:foobar#" type="fcrepo-solr">
                  <test name="Simple ingest test">
                  </test>
                 </testsuite>'''

        fname = self.write_test_file( xml )
        rvalue = vt.validate_testsuite_file( fname )
        self.assertEqual( None, rvalue )

    def test_wrong_rootname_returns_none( self ):
        """
        Tests if 'None' is returned if root node is not testsuite in input file.
        """
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
                 <foobar xmlns="info:testsuite#" type="fcrepo-solr">
                  <test name="Simple ingest test">
                  </test>
                 </foobar>'''

        fname = self.write_test_file( xml )
        rvalue = vt.validate_testsuite_file( fname )
        self.assertEqual( None, rvalue )

    def test_no_type_attribute_returns_none( self ):
        """
        tests whether 'None' is returned if the root not dosn't have a type attribute.
        """
        self.assertTrue(True)
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
                 <testsuite xmlns="info:testsuite#" >
                  <test name="Simple ingest test">
                  </test>
                 </testsuite>'''

        fname = self.write_test_file( xml )
        rvalue = vt.validate_testsuite_file( fname )
        self.assertEqual( None, rvalue )

    def test_wrong_nodenames_returns_none( self ):
        """
        Tests if other nodes than setup and test returns 'None'.
        """
        self.assertTrue(True)
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
                 <testsuite xmlns="info:testsuite#" type="fcrepo-solr">
                  <foo name="Simple ingest test">
                  </foo>
                 </testsuite>'''

        fname = self.write_test_file( xml )
        rvalue = vt.validate_testsuite_file( fname )
        self.assertEqual( None, rvalue )

    def test_multiple_setup_nodes_returns_none( self ):
        """
        Tests whether multiple setup nodes results in 'None' returned.
        """
        self.assertTrue(True)
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
                 <testsuite xmlns="info:testsuite#" type="fcrepo-solr">
                  <setup></setup>
                  <setup></setup>
                  <test name="Simple ingest test">
                  </test>
                 </testsuite>'''

        fname = self.write_test_file( xml )
        rvalue = vt.validate_testsuite_file( fname )
        self.assertEqual( None, rvalue )

    def test_valid_xml_file_returns_expected_xml( self ):
        """
        Tests whether valid xml file results in expected xml.
        """
        self.assertTrue(True)
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
                 <testsuite xmlns="info:testsuite#" type="fcrepo-solr">
                  <setup></setup>
                  <test name="Simple ingest test">
                  </test>
                 </testsuite>'''

        fname = self.write_test_file( xml )
        rvalue = vt.validate_testsuite_file( fname )

        self.assertEqual( "fcrepo-solr",
                          rvalue.xpath( "/ns:testsuite",
                                        namespaces = {'ns': 'info:testsuite#'} )[0].get( 'type' ) )
        self.assertEqual( "Simple ingest test",
                          rvalue.xpath( "/ns:testsuite/ns:test",
                                        namespaces = {'ns': 'info:testsuite#'} )[0].get( 'name' ) )

if __name__ == '__main__':
    unittest.main()
