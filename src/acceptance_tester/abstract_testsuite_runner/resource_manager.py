#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""
:mod:`acceptance_tester.abstract_testsuite_runner.resource_manager` -- Abstract resource manager
================================================================================================

==========================
Resource Manager Interface
==========================

This abstract resource manager should be inherited by test runner
code. Each test type can specify a resource manager class, and if
this class is inherited, the acceptance tester will work.

The resource manager is initialized before any tests are run, so any
code that should only run once should be placed here. A reference to
the created resource manager are passed along to the tests. No
synchronization is provided, so if this is needed it should be
implemented in rhe resource manager.
"""

class AbstractResourceManager( object ):
    """
    Abstract resource manager. can be implemented by testrunner.
    """

    def __init__(self, resource_folder, tests, use_preloaded, config_preloaded):
        """
        Initializes the resource manager.

        This constructor is called before any tests are run.

        :param resource_folder:
            Folder that resource manager can use as build folder.
            Folder exists when this constructor is called.
        :type resource_folder:
            string
        :param tests:
            Dictionary containing information about the tests that are
            going to be executed. The contents of the dictionary are
            as follows:

            #. **build-folder**

               The tests candidate build folder (is not final at this point. SHOULD NOT BE USED).

            #. **id**

               Unique int identifier for this test.

            #. **report-file**

               The report file used for this test run.

            #. **test-suite**

               The absolute path to the testsuite containing this test.

            #. **type**

               The type dict for this test.

            #. **type-name**

               The name of the type of this test.

            #. **verbose**

               Boolean flag. If true verbose output should be printed to stdout.

            #. **xml**

               The xml specifying this test execution.

        :type tests:
            dict
        :param use_preloaded:
            Flag indicating if resource manager is allowed to use preloaded
            resources.
        :type use_preloaded:
            boolean
        :param config_preloaded:
            If set, this is a path to a configfile to find resources
        :type config_preloaded:
            string
        """
        raise NotImplemented()

    def shutdown(self):
        pass

