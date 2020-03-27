#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""
:mod:`acceptance_tester.supported_test_types` -- Known test types
=================================================================

====================
Supported Test Types
====================

Contains the types of test acceptance-tester can handle.

The :data:`TYPES` contains the known test types that can be handled.

The key of an entry is the name of the test type. The type attribute
of the testsuite node in a testsuite xml file, is used to lookup in
the :data:`TYPES` dictionary.

Each type must have at least a 'test-runner' entry. If the xsd entry
is present, the tests are validated against the schema. If a
resource-manager is present, this is initialzedd before any tests are
run, and each test have a reference to the resource-manager. Note: no
synchronization takes place. This must be implemented by inheriter if
necessary.

The specified classes are loaded at dynamically, so testrunners for
the testtypes that are not relevant need not be on the pythonpath and
this loadable.

Test type entrys
----------------

**test-runner**

The class that runs each test. This **must** inherit from
:class:`acceptance-tester.abstract_testsuite_runner.test_runner`

**resource_manager**

This entry is optional.
If present should be a class that inherits from
:class:`acceptance-tester.abstract_testsuite_runner.resource_manager`

**xsd**

This entry is optional.
If present it should point to a xsd file to validate the tests
against, and it must be a path inside the package relative to the
src/acceptance_tester folder.

:data TYPES:
    The dictionary containing classes and xsd for each test type.

"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))

TYPES = {'addi-fcrepo':    {'xsd': None,
                            'resource-manager': "addi_corepo_testrunner.resource_manager.ResourceManager",
                            'test-runner': "addi_corepo_testrunner.testrunner.TestRunner"},
         'hive-fcrepo':    {'xsd': None,
                            'resource-manager': "hive_corepo_testrunner.resource_manager.ResourceManager",
                            'test-runner': "hive_corepo_testrunner.testrunner.TestRunner"},
         'fcrepo-solr':    {'xsd': None,
                            'resource-manager': "corepo_solr_testrunner.resource_manager.ResourceManager",
                            'test-runner': "corepo_solr_testrunner.testrunner.TestRunner"},
         'convert':        {'xsd': None,
                            'resource-manager': "convert_testrunner.resource_manager.ResourceManager",
                            'test-runner': "convert_testrunner.testrunner.TestRunner"},
         'jsconvert':      {'xsd': None,
                            'resource-manager': "jsshell_convert_testrunner.resource_manager.ResourceManager",
                            'test-runner': "jsshell_convert_testrunner.testrunner.TestRunner"},
         'holdings':       {'xsd': None,
                            'resource-manager': "holdings_testrunner.resource_manager.ResourceManager",
                            'test-runner': "holdings_testrunner.testrunner.TestRunner"},
         'suggestion':     {'xsd': None,
                            'resource-manager': "suggestion_testrunner.resource_manager.ResourceManager",
                            'test-runner': "suggestion_testrunner.testrunner.TestRunner"},
         'rawrepo':        {'xsd': None,
                            'resource-manager': "rawrepo_indexer_testrunner.resource_manager.ResourceManager",
                            'test-runner': "rawrepo_indexer_testrunner.testrunner.TestRunner"},
         'holdings-items': {'xsd': None,
                            'resource-manager': "holdings_items_testrunner.resource_manager.ResourceManager",
                            'test-runner': "holdings_items_testrunner.testrunner.TestRunner"},
         'holdings-collections': {'xsd': None,
                            'resource-manager': "holdings_collections_testrunner.resource_manager.ResourceManager",
                            'test-runner': "holdings_collections_testrunner.testrunner.TestRunner"}

         }

