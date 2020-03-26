#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""
:mod:`acceptance_tester.framework.load_testrunner` -- loads a testrunner
========================================================================

===============
Load testrunner
===============

This module contains the function load_testrunner, that reads a
testrunner definition as specified in the :mod:`supported_types`
module, and initializes the relevant classes and validates them.
"""

import logging
from nose.tools import nottest

from acceptance_tester.abstract_testsuite_runner.resource_manager import AbstractResourceManager
from acceptance_tester.abstract_testsuite_runner.test_runner import TestRunner as AbstractTestRunner


class NullHandler( logging.Handler ):
    """ Nullhandler for logging. """

    def emit( self, record ):
        pass

### define logger
logger = logging.getLogger( "dbc."+__name__ )
logger.addHandler( NullHandler() )


def _load_class( cls ):
    """
    Imports the class from the module containing it, and returns the class.
    """
    i = cls.rfind(".")
    exec_str = "from %s import %s"%( cls[:i], cls[i+1:] )
    logger.debug( "Executing statement '%s'"%exec_str )
    exec( exec_str )
    return eval( cls[i+1:] )


def _validate_subclass_type( cls, expected_subcls ):
    """
    Validates inheritance. An error is raised if cls is not a subclass
    of expected_subcls.
    """
    if not issubclass( cls, expected_subcls ):
        raise NotImplementedError( "class %s is not a subclass of %s"%( cls, expected_subcls ) )


@nottest
def load_testrunner( testrunner_definition, testrunner_config=None ):
    """
    Dynamically load the testrunner resources defined in testrunner_definition.

    :param testrunner_definition:
        The testrunner to load. This should be a dictionary defining
        which resources should be initialized. This must contain a
        test-runner entry, and can contain a resource-manager and a
        xsd entry as well. see :mod:`supported_types` for details
    :type testrunner_definition:
        dict

    :returns:
       Dictionary with the specific loaded classes, and path too
       specific files.  If no resource-manager or xsd entry was found
       in the definition, or the value was None, the entry is NOT
       added to the returned dictionary.
    """

    testrunner = _load_class( testrunner_definition['test-runner'] )
    _validate_subclass_type( testrunner, AbstractTestRunner )
    retval = { 'test-runner': testrunner }
    testrunner.config = testrunner_config

    if 'resource-manager' in testrunner_definition and testrunner_definition['resource-manager'] != None:
        resource_manager = _load_class( testrunner_definition['resource-manager'] )
        _validate_subclass_type( resource_manager, AbstractResourceManager )
        retval['resource-manager'] = resource_manager

    if 'xsd' in testrunner_definition and testrunner_definition['xsd'] != None:
        retval['xsd'] = testrunner_definition['xsd']

    return retval
