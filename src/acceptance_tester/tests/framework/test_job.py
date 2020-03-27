#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert( 0, os.path.dirname( os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( sys.argv[0] ) ) ) ) ) )
import acceptance_tester.framework.job as job
from acceptance_tester.abstract_testsuite_runner.test_runner import TestRunner


def mock_sync_stdout_write( string ):
    pass

def mock_sync_file_append( path, string ):
    pass

job._sync_file_append = mock_sync_file_append
job._sync_stdout_write = mock_sync_stdout_write


class  MockRunner( TestRunner ):

    def run_test( self, test_xml, build_folder, resource_manager ):
        pass


class TestJob( unittest.TestCase ):

    def setUp( self ):

        self.test_folder = tempfile.mkdtemp()
        self.arg = { "id": 10,
                     "build-folder": self.test_folder,
                     "documentation": {},
                     "name": "foo",
                     "test-suite": "bar",
                     "report-file": "baz",
                     "resource-manager": None,
                     "type": { "test-runner": MockRunner},
                     "type-name": "type name",
                     "verbose": False,
                     "xml": "<test-xml>msg</test-xml>",
                     "name": "foo",
                     "log-folder": self.test_folder,
                     "color": False }

    def tearDown( self ):
        shutil.rmtree( self.test_folder )

    def test_that_status_is_SUCCESS_if_no_errors_or_failures_are_reported( self ):
        """
        Tests that status is 'SUCCESS' if no errors or failures were reported.
        """

        def local_run_test( self, test_xml, build_folder, resource_manager ):
            pass

        self.arg['type']['test-runner'].run_test = local_run_test
        result = job.job( self.arg )
        self.assertEqual( 'SUCCESS', job.job( self.arg )['status'] )

    def test_that_status_is_ERROR_if_error_is_reported( self ):
        """
        Tests whether status is 'ERROR' if error is reported.
        """

        def local_run_test( self, test_xml, build_folder, resource_manager ):
            self.errors.append( "error encountered" )

        self.arg['type']['test-runner'].run_test = local_run_test
        result = job.job( self.arg )
        self.assertEqual( 'ERROR', job.job( self.arg )['status'] )

    def test_that_status_is_FAILURE_if_failure_is_reported( self ):
        """
        Tests whether status is 'FAILURE' if error is reported.
        """

        def local_run_test( self, test_xml, build_folder, resource_manager ):
            self.failures.append( "failure encountered" )

        self.arg['type']['test-runner'].run_test = local_run_test
        result = job.job( self.arg )
        self.assertEqual( 'FAILURE', job.job( self.arg )['status'] )

    def test_exception_is_reported_as_ERROR( self ):
        """
        Tests whether a raised exception is caught an reported as an ERROR.
        """

        def local_run_test( self, test_xml, build_folder, resource_manager ):
            raise RuntimeError( "exception encountered" )

        self.arg['type']['test-runner'].run_test = local_run_test
        result = job.job( self.arg )
        self.assertEqual( 'ERROR', job.job( self.arg )['status'] )


if __name__ == '__main__':
    unittest.main()
