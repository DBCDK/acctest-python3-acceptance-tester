#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""
:mod:`acceptance_tester.cli` -- commandline interface for acceptance-tester
===========================================================================

=====================
Commandline Interface
=====================

The **suite_test** script must be provided with a testfolder as the
first (and only) argument.  The testfolder is looked through
recursively for testsuite files, which are used to run the tests. The
acceptance tester can only test of one test type on each run.


Commandline options
-------------------

None of the options are mandatory, they all have sane default values.

.. cmdoption:: --build-folder <build-folder>

   Folder to place test builds in.

.. cmdoption:: --resource-folder <resource-folder>

   The folder for the resource manager to use.

.. cmdoption:: --test-result-folder <test-result-folder>

   Folder to place test results in.

.. cmdoption:: --report-file <report-file>

   Path to place test report file at.

.. cmdoption:: --pool-size <pool-size>

   Number of concurrent tests to run.

.. cmdoption:: --verbose <verbose>

   Verbose output to stdout.

.. cmdoption:: --use-preloaded-resources

   Allows resource manager to use preloaded resources.

.. cmdoption:: --port-range

   Specifies in which range the resource_manager should allocate ports
   from. the format is start-end, where start and end are integers

**Log options**

.. cmdoption:: --loglevel <loglevel>

   Specifies log level.

.. cmdoption:: --logfile <logfile>

   Specifies log file.

.. cmdoption:: --filemode <filemode>

   Overwrite (w) logfile or append (a).

.. cmdoption:: --fileformat <fileformat>

   Specify format for file logs.

.. cmdoption:: --dateformat <dateformat>

   Specify format for dates in logs.

"""

from optparse import OptionParser

import os

import dbc_python.utils.basic_logger as basic_logger
import framework.suite_tester as suite_tester


def parse_testfile_file( file ):

    fh = open( file )
    content = map( lambda x: x.strip(), fh.readlines() )
    fh.close()
    return content


def cli():

    usage="Runs acceptance tester with testsuite files found in testfolder."

    parser = OptionParser( usage="%prog [options] testfolder\n" + usage )

    default_build_folder = 'build-folder'
    default_resource_folder = 'resources'
    default_test_result_folder = 'test-results'
    default_report_file = 'test-report.txt'
    default_log_file = 'logs.zip'
    default_pool_size = 8
    default_verbose = False
    default_use_preloaded_resources = False

    parser.add_option("--build-folder", type="string", action="store", dest="build_folder",
                      default=default_build_folder,
                      help="Folder to use for test builds. Default is '%s'"% default_build_folder )

    parser.add_option("--resource-folder", type="string", action="store", dest="resource_folder",
                      default=default_resource_folder,
                      help="The folder for the resource manager to use. Deafult is '%s'"%default_resource_folder )

    parser.add_option("--test-result-folder", type="string", action="store", dest="test_result_folder",
                      default=default_test_result_folder,
                      help="Folder to place test results in. Default is '%s'"% default_test_result_folder )

    parser.add_option("--report-file", type="string", action="store", dest="report_file",
                      default=default_report_file,
                      help="Path to place test report file at. Default is '%s'"% default_report_file )

    parser.add_option("--log-file", type="string", action="store", dest="log_file",
                      default=default_log_file,
                      help="Path to logfile archive. Default is '%s'"% default_log_file )

    parser.add_option("--testrunner-config", type="string", action="store", dest="testrunner_config",
                      default=None,
                      help="May be used to configure testrunner instance.")

    parser.add_option("--pool-size", type="string", action="store", dest="pool_size",
                      default=default_pool_size,
                      help="Number of concurrent tests to run. Default is '%s'"% default_pool_size )

    parser.add_option("--verbose", action="store_true", dest="verbose",
                      default=default_verbose,
                      help="Verbose output to stdout." )

    parser.add_option("--use-configured-resources", type="string", action="store", dest="configured_resources",
                      help="Allows resource manager to use configured resources." )

    parser.add_option("--use-preloaded-resources", action="store_true", dest="use_preloaded_resources",
                      default=default_use_preloaded_resources,
                      help="Allows resource manager to use preloaded resources." )

    parser.add_option("--port-range", type="string", action="store", dest="port_range",
                      default="12000-13000",
                      help="Specifies in which range the resource_manager should allocate ports" + \
                      "from. the format is start-end, where start and end are integers" )

    parser.add_option("-f", "--file", action="store", dest="file",
                      help="If file is specified, the testfiles in this file are run" )

    parser.add_option("-n", "--no-clean", action="store_true", dest="no_clean",
                      help="If specified, build folder is not removed after test" )

    parser.add_option("-c", "--color", action="store_true", dest="color", default=False,
                      help="Uses ansi colors to enhance output" )

    parser.add_option("--loglevel", type="string", action="store",
                      dest="loglevel", default='debug',
                      help="Specifies log level. Default is '%s'"%'debug' )
    parser.add_option("--logfile", type="string", action="store", dest="logfile",
                      default='suite-test.log',
                      help="Specifies log file. Default is '%s'"%'suite-test.log'  )
    parser.add_option("--filemode", type="string", action="store", dest="filemode",
                      default=basic_logger.FILEMODE,
                      help="Overwrite logfile or append. Options are: %s. Default is %s"
                      % ( basic_logger.FILEMODES, basic_logger.FILEMODE ) )
    parser.add_option("--fileformat", type="string", action="store", dest="fileformat",
                      default="%(name)-12s<%(process)d>%(asctime)s %(levelname)s %(message)s",
                      help="Specify format for file logs." )
    parser.add_option("--dateformat", type="string", action="store", dest="dateformat",
                      default=basic_logger.DATE_FORMAT,
                      help="Specify format for dates in logs. Default is %s" % basic_logger.DATE_FORMAT )

    ( options, args ) = parser.parse_args()

    basic_logger.Basic_logger( log_level = options.loglevel,
                               file_format = options.fileformat,
                               date_format = options.dateformat,
                               log_filename = options.logfile,
                               file_mode = options.filemode,
                               console = False )

    test_targets = []
    print "option", options.file
    if options.file != None:
        test_targets += parse_testfile_file( os.path.abspath( options.file ) )

    test_targets += args

    if len( test_targets ) == 0:
        err_msg = "Please supply a testfile or testfolder."
        raise RuntimeError( err_msg )

    suite_tester.run( test_targets,
                      options.build_folder,
                      options.resource_folder,
                      options.test_result_folder,
                      options.report_file,
                      options.log_file,
                      options.testrunner_config,
                      options.pool_size,
                      options.verbose,
                      options.use_preloaded_resources,
                      options.configured_resources,
                      options.port_range,
                      options.color,
                      options.no_clean)
