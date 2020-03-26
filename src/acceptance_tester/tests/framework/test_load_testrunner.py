#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
import unittest
from nose.tools import nottest
import acceptance_tester.framework.load_testrunner as lt
from acceptance_tester.abstract_testsuite_runner.test_runner import TestRunner as AbstractTestRunner
from acceptance_tester.abstract_testsuite_runner.resource_manager import AbstractResourceManager


class MockRunner( AbstractTestRunner ):

    @nottest
    def run_test( self, test_xml, build_folder, resource_manager ):
        pass


class MockResourceManager( AbstractResourceManager ):

    def __init__( self ):
        pass


class TestLoadTestrunner( unittest.TestCase ):

    def test_load_class_loads_module_as_expected( self ):
        """ Test whether load class, imports class as expected
        """
        cls_name = "acceptance_tester.framework.load_testrunner.NullHandler"
        cls = lt._load_class( cls_name )
        self.assertEqual( "NullHandler", cls.__name__ )

    def test_validate_subclass_does_not_raise_if_subclass_inherits( self ):
        """ Test whether the method returns without raising a NotImplementedError if cls is a subclass.
        """
        lt._validate_subclass_type( MockRunner, AbstractTestRunner )

    def test_validate_subclass_raises_if_subclass_does_not_inherit( self ):
        """ Test whether a NotImplementedError is raised if cls is not a subclass of expected_subcls.
        """
        self.failUnlessRaises( NotImplementedError,
                               lt._validate_subclass_type, TestLoadTestrunner, AbstractTestRunner )

    def test_load_testrunner_expected_testrunner_is_present_in_result( self ):
        """ Test whether the expected testrunner is present in the result
        """
        test_type = { 'test-runner': "acceptance_tester.tests.framework.test_load_testrunner.MockRunner" }
        result = lt.load_testrunner( test_type, "testrunner-config" )
        self.assertEqual( "MockRunner", result['test-runner'].__name__ )

    def test_load_testrunner_expected_resource_manager_is_present_in_result( self ):
        """ Test whether the expected resource manager is present in the result
        """
        test_type = { 'test-runner': "acceptance_tester.tests.framework.test_load_testrunner.MockRunner",
                      'resource-manager': "acceptance_tester.tests.framework.test_load_testrunner.MockResourceManager" }
        result = lt.load_testrunner( test_type, "testrunner-config" )
        self.assertEqual( "MockRunner", result['test-runner'].__name__ )
        self.assertEqual( "MockResourceManager", result['resource-manager'].__name__ )

    def test_load_testrunner_expected_xsd_is_present_in_result( self ):
        """ Test whether the expected xsd is present in the result
        """
        test_type = { 'test-runner': "acceptance_tester.tests.framework.test_load_testrunner.MockRunner",
                      'xsd': "path/to/xsd/file" }
        result = lt.load_testrunner( test_type, "testrunner-config" )
        self.assertEqual( "MockRunner", result['test-runner'].__name__ )
        self.assertEqual( "path/to/xsd/file", result['xsd'] )

    def test_load_testrunner_no_resource_manager_is_present_in_result_if_not_present_in_definition( self ):
        """ Test that no resource-manager is present in the result, if not present in the testdefinition
        """
        test_type = { 'test-runner': "acceptance_tester.tests.framework.test_load_testrunner.MockRunner",
                      'xsd': "path/to/xsd/file" }
        result = lt.load_testrunner( test_type, "testrunner-config" )
        self.assertTrue( 'resource-manager' not in result )

    def test_load_testrunner_no_xsd_is_present_in_result_if_not_present_in_definition( self ):
        """ Test that no xsd is present in the result, if not present in the testdefinition
        """
        test_type = { 'test-runner': "acceptance_tester.tests.framework.test_load_testrunner.MockRunner",
                      'resource-manager': "acceptance_tester.tests.framework.test_load_testrunner.MockResourceManager" }
        result = lt.load_testrunner( test_type, "testrunner-config" )
        self.assertTrue( 'xsd' not in result )
