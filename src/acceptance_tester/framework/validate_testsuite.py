#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""
:mod:`acceptance_tester.framework.validate_testsuite` -- Validates testsuite file

=======================
Validate testsuite file
=======================

If this validation returns true the xml file should be valid for
use with the acceptance_tester.

This is not a real xsd validation, only the root node and its
children are checked. If full xsd validation is necessary, this
should be placed in the specific test runner it should apply to.

The files are validated against this pseudo xsd

.. code-block:: xml

   <xsd:schema targetNamespace='info:testsuite#'
        xmlns:xsd='http://www.w3.org/2001/XMLSchema'
        elementFormDefault='qualified'>

   <xsd:element name='testsuite'>
      <xsd:annotation>
         <xsd:documentation>
            test occurence is unbounded, i.e. you can have as many tests as
            you want in the root element. The type attribute is required.
         </xsd:documentation>
      </xsd:annotation>

      <xsd:complexType>
         <xsd:sequence maxOccurs='1'>
            <xsd:element name='setup' type='setupType' />
            <xsd:choice maxOccurs='unbounded'>
            <xsd:element name='test' type='testType'/>
            </xsd:choice>
         </xsd:sequence>
         <xsd:attribute name='type' use='required' type='xsd:string'/>
      </xsd:complexType>
   </xsd:element>


So in short the following points must be in order, before a xml
file can be validated.

#. The namespace for the testsuite must be 'info:testsuite'.
#. The root node is called testsuite.

#. The root node must have an attribute called type, Used to
   choose which test run ner to use.

#. Children of the root node can either be a node called 'setup' or 'test'.
#. Only one 'setup' node is allowed

"""
import logging
from lxml import etree
from nose.tools import nottest

import io


class NullHandler( logging.Handler ):
    """
    Nullhandler for logging.
    """

    def emit( self, record ):
        pass

### define logger
logger = logging.getLogger( "dbc."+__name__ )
logger.addHandler( NullHandler() )


@nottest
def validate_testsuite_file( file ):
    """
    Validates a testsuite file.

    :param file:
        The xml file to validate
    :type file:
        string

    :return:
        xml if file is a valid testsuite xml file, None otherwise
    """
    namespace = "{info:testsuite#}"

    parser = etree.XMLParser( remove_blank_text=True, encoding="UTF-8" )

    xml = None
    try:
        fh = open( file, "rb" )
        content = fh.read()
        fh.close()
        #logger.debug( "Content: %s", content )

        xml = etree.parse( io.BytesIO( content ), parser )

    except Exception:
        pass

    if not xml:
        logger.debug( "Could not read file '%s', is it valid xml?"%file )
        return None

    root = xml.getroot()
    if root.tag != "%stestsuite"%namespace:
        logger.debug( "Root tag is not testsuite in file '%s'"%file )
        return None

    if not root.get( "type" ):
        logger.debug( "testsuite node have no type attribute in file '%s'"%file )
        return None

    number_of_setup_nodes = 0
    for child in [x for x in root if x.tag != etree.Comment]:

        if child.tag == "%ssetup"%namespace:
            number_of_setup_nodes += 1
        elif child.tag != "%stest"%namespace:
            logger.debug( "Found child '%s' in file '%s', only test and setup nodes are allowed"%( child.tag, file ) )
            return None

    if number_of_setup_nodes > 1:
        logger.debug( "Found more than one setup node in file '%s'"%file )
        return None

    logger.debug( "xml found in file '%s' is valid testsuite xml"%file )
    return xml
