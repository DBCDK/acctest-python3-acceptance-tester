#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
import datetime
import unittest
import os
from lxml import etree
import shutil
import io
import tempfile
from acceptance_tester.framework.rst_creator import TocTree
import acceptance_tester.framework.rst_creator as rst_creator

parser = etree.XMLParser( remove_blank_text=True, encoding="UTF-8" )


def normalize( xml ):
    return etree.tostring( etree.parse( io.StringIO( xml ), parser ),
                           pretty_print=True, encoding="UTF-8" )


create_rst_testdata_all_fields = {'status': 'SUCCESS', 'xml': b'<wrapping name="cd is soundtrack of movie">\n  <setup xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi">\n    <fc:fcrepo type="normal"/>\n    <ad:addiService/>\n  </setup>\n  <test xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi" name="cd is soundtrack of movie">\n    <description>This example shows that relations between a movie and its soundtrack can be created</description>\n    <given>A cd</given>\n    <when>is stored in the repository in which is the movie to which it is the soundtrack</when>\n    <then>relations between the cd and the movie are created</then>\n    <fc:ingest type="folder" value="../../../../fedora-test-objects/soundtrack_movie" expected="2"/>\n    <ad:addJob pid="unit:35"/>\n    <fc:checkAddi subject="unit:13" predicate="http://oss.dbc.dk/rdf/dbcaddi#hasSoundtrack" object="unit:35"/>\n    <fc:checkAddi subject="unit:35" predicate="http://oss.dbc.dk/rdf/dbcaddi#isSoundtrackOfMovie" object="unit:13"/>\n  </test>\n</wrapping>\n', 'errors': [], 'status-msg': "Test 'cd is soundtrack of movie' status: SUCCESS.", 'test-suite': '/home/shm/repos/svn.dbc.dk/repos/addi-fcrepo-acctest/trunk/testsuites/verified/addirelations/soundtrack/soundtrack_of_movie.xml', 'documentation': {'then': 'relations between the cd and the movie are created', 'given': 'A cd', 'when': 'is stored in the repository in which is the movie to which it is the soundtrack', 'description': 'This example shows that relations between a movie and its soundtrack can be created'}, 'type-name': 'addi-fcrepo', 'summary': ['------------------------------------------------------------------------------------------------------------------------', 'Test Summary:', "  testfile: '/home/shm/repos/svn.dbc.dk/repos/addi-fcrepo-acctest/trunk/testsuites/verified/addirelations/soundtrack/soundtrack_of_movie.xml'", "  testname: 'cd is soundtrack of movie'", '  status: SUCCESS', '  duration: 1:34 minutes', '------------------------------------------------------------------------------------------------------------------------'], 'time': datetime.timedelta(0, 94, 50464), 'failures': [], 'build-folder': '/home/shm/repos/svn.dbc.dk/repos/acceptance-tester-dev/trunk/build-folder/soundtrack_of_movie___cd_is_soundtrack_of_movie', 'name': 'cd is soundtrack of movie'}

create_rst_testdata_missing_field = {'status': 'SUCCESS', 'xml': b'<wrapping name="cd is soundtrack of movie">\n  <setup xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi">\n    <fc:fcrepo type="normal"/>\n    <ad:addiService/>\n  </setup>\n  <test xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi" name="cd is soundtrack of movie">\n    <description>This example shows that relations between a movie and its soundtrack can be created</description>\n   <when>is stored in the repository in which is the movie to which it is the soundtrack</when>\n    <then>relations between the cd and the movie are created</then>\n    <fc:ingest type="folder" value="../../../../fedora-test-objects/soundtrack_movie" expected="2"/>\n    <ad:addJob pid="unit:35"/>\n    <fc:checkAddi subject="unit:13" predicate="http://oss.dbc.dk/rdf/dbcaddi#hasSoundtrack" object="unit:35"/>\n    <fc:checkAddi subject="unit:35" predicate="http://oss.dbc.dk/rdf/dbcaddi#isSoundtrackOfMovie" object="unit:13"/>\n  </test>\n</wrapping>\n', 'errors': [], 'status-msg': "Test 'cd is soundtrack of movie' status: SUCCESS.", 'test-suite': '/home/shm/repos/svn.dbc.dk/repos/addi-fcrepo-acctest/trunk/testsuites/verified/addirelations/soundtrack/soundtrack_of_movie.xml', 'documentation': {'then': 'relations between the cd and the movie are created', 'given': 'A cd', 'when': 'is stored in the repository in which is the movie to which it is the soundtrack', 'description': 'This example shows that relations between a movie and its soundtrack can be created'}, 'type-name': 'addi-fcrepo', 'summary': ['------------------------------------------------------------------------------------------------------------------------', 'Test Summary:', "  testfile: '/home/shm/repos/svn.dbc.dk/repos/addi-fcrepo-acctest/trunk/testsuites/verified/addirelations/soundtrack/soundtrack_of_movie.xml'", "  testname: 'cd is soundtrack of movie'", '  status: SUCCESS', '  duration: 1:34 minutes', '------------------------------------------------------------------------------------------------------------------------'], 'time': datetime.timedelta(0, 94, 50464), 'failures': [], 'build-folder': '/home/shm/repos/svn.dbc.dk/repos/acceptance-tester-dev/trunk/build-folder/soundtrack_of_movie___cd_is_soundtrack_of_movie', 'name': 'cd is soundtrack of movie'}


view_testdata = {('/home/shm/repos/svn.dbc.dk/repos/addi-fcrepo-acctest/trunk/testsuites/verified/addirelations/soundtrack/soundtrack_of_game.xml', 'cd is soundtrack of movie'): ('soundtrack_of_game___cd_is_soundtrack_of_movie', 'cd is soundtrack of movie\n-------------------------\n\n**Description:**\n\nThis example shows that relations between a game and its soundtrack can be created\n\n**Given:**\n\nA cd\n\n**When:**\n\nis stored in the repository in which is the game to which it is the soundtrack\n\n**Then:**\n\nrelations between the cd and the game is created\n\n``testsuite: soundtrack_of_game.xml``\n\n.. code-block:: xml\n\n   <wrapping name="cd is soundtrack of movie">\n     <setup xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi">\n       <fc:fcrepo type="normal"/>\n       <ad:addiService/>\n     </setup>\n     <test xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi" name="cd is soundtrack of movie">\n       <description>This example shows that relations between a game and its soundtrack can be created</description>\n       <given>A cd</given>\n       <when>is stored in the repository in which is the game to which it is the soundtrack</when>\n       <then>relations between the cd and the game is created</then>\n       <fc:ingest type="folder" value="../../../../fedora-test-objects/soundtrack_game" expected="2"/>\n       <ad:addJob pid="unit:30"/>\n       <fc:checkAddi subject="unit:20" predicate="http://oss.dbc.dk/rdf/dbcaddi#hasSoundtrack" object="unit:30"/>\n       <fc:checkAddi subject="unit:30" predicate="http://oss.dbc.dk/rdf/dbcaddi#isSoundtrackOfGame" object="unit:20"/>\n     </test>\n   </wrapping>\n   '), ('/home/shm/repos/svn.dbc.dk/repos/addi-fcrepo-acctest/trunk/testsuites/verified/addirelations/soundtrack/soundtrack_of_movie.xml', 'cd is soundtrack of movie'): ('soundtrack_of_movie___cd_is_soundtrack_of_movie', 'cd is soundtrack of movie\n-------------------------\n\n**Description:**\n\nThis example shows that relations between a movie and its soundtrack can be created\n\n**Given:**\n\nA cd\n\n**When:**\n\nis stored in the repository in which is the movie to which it is the soundtrack\n\n**Then:**\n\nrelations between the cd and the movie are created\n\n``testsuite: soundtrack_of_movie.xml``\n\n.. code-block:: xml\n\n   <wrapping name="cd is soundtrack of movie">\n     <setup xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi">\n       <fc:fcrepo type="normal"/>\n       <ad:addiService/>\n     </setup>\n     <test xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi" name="cd is soundtrack of movie">\n       <description>This example shows that relations between a movie and its soundtrack can be created</description>\n       <given>A cd</given>\n       <when>is stored in the repository in which is the movie to which it is the soundtrack</when>\n       <then>relations between the cd and the movie are created</then>\n       <fc:ingest type="folder" value="../../../../fedora-test-objects/soundtrack_movie" expected="2"/>\n       <ad:addJob pid="unit:35"/>\n       <fc:checkAddi subject="unit:13" predicate="http://oss.dbc.dk/rdf/dbcaddi#hasSoundtrack" object="unit:35"/>\n       <fc:checkAddi subject="unit:35" predicate="http://oss.dbc.dk/rdf/dbcaddi#isSoundtrackOfMovie" object="unit:13"/>\n     </test>\n   </wrapping>\n   '), ('/home/shm/repos/svn.dbc.dk/repos/addi-fcrepo-acctest/trunk/testsuites/verified/addirelations/soundtrack/game_has_soundtrack.xml', 'game has soundtrack'): ('game_has_soundtrack___game_has_soundtrack', 'game has soundtrack\n-------------------\n\n**Description:**\n\nThis example shows that relations between a game and its soundtrack can be created\n\n**Given:**\n\nA game\n\n**When:**\n\nis stored in the repository in which is its soundtrack\n\n**Then:**\n\nrelations between the game and the soundtrack are created\n\n``testsuite: game_has_soundtrack.xml``\n\n.. code-block:: xml\n\n   <wrapping name="game has soundtrack">\n     <setup xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi">\n       <fc:fcrepo type="normal"/>\n       <ad:addiService/>\n     </setup>\n     <test xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi" name="game has soundtrack">\n       <description>This example shows that relations between a game and its soundtrack can be created</description>\n       <given>A game</given>\n       <when>is stored in the repository in which is its soundtrack</when>\n       <then>relations between the game and the soundtrack are created</then>\n       <fc:ingest type="folder" value="../../../../fedora-test-objects/soundtrack_game" expected="2"/>\n       <ad:addJob pid="unit:20"/>\n       <fc:checkAddi subject="unit:20" predicate="http://oss.dbc.dk/rdf/dbcaddi#hasSoundtrack" object="unit:30"/>\n       <fc:checkAddi subject="unit:30" predicate="http://oss.dbc.dk/rdf/dbcaddi#isSoundtrackOfGame" object="unit:20"/>\n     </test>\n   </wrapping>\n   '), ('/home/shm/repos/svn.dbc.dk/repos/addi-fcrepo-acctest/trunk/testsuites/verified/addirelations/soundtrack/movie_has_soundtrack.xml', 'movie has soundtrack'): ('movie_has_soundtrack___movie_has_soundtrack', 'movie has soundtrack\n--------------------\n\n**Description:**\n\nThis example shows that relations between a movie and its soundtrack can be created\n\n**Given:**\n\nA movie\n\n**When:**\n\nis stored in the repository in which is its soundtrack\n\n**Then:**\n\nrelations between the movie and the soundtrack are created\n\n``testsuite: movie_has_soundtrack.xml``\n\n.. code-block:: xml\n\n   <wrapping name="movie has soundtrack">\n     <setup xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi">\n       <fc:fcrepo type="normal"/>\n       <ad:addiService/>\n     </setup>\n     <test xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi" name="movie has soundtrack">\n       <description>This example shows that relations between a movie and its soundtrack can be created</description>\n       <given>A movie</given>\n       <when>is stored in the repository in which is its soundtrack</when>\n       <then>relations between the movie and the soundtrack are created</then>\n       <fc:ingest type="folder" value="../../../../fedora-test-objects/soundtrack_movie" expected="2"/>\n       <ad:addJob pid="unit:13"/>\n       <fc:checkAddi subject="unit:13" predicate="http://oss.dbc.dk/rdf/dbcaddi#hasSoundtrack" object="unit:35"/>\n       <fc:checkAddi subject="unit:35" predicate="http://oss.dbc.dk/rdf/dbcaddi#isSoundtrackOfMovie" object="unit:13"/>\n     </test>\n   </wrapping>\n   ')}

testdata = [{'status': 'SUCCESS', 'xml': b'<wrapping name="cd is soundtrack of movie">\n  <setup xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi">\n    <fc:fcrepo type="normal"/>\n    <ad:addiService/>\n  </setup>\n  <test xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi" name="cd is soundtrack of movie">\n    <description>This example shows that relations between a movie and its soundtrack can be created</description>\n    <given>A cd</given>\n    <when>is stored in the repository in which is the movie to which it is the soundtrack</when>\n    <then>relations between the cd and the movie are created</then>\n    <fc:ingest type="folder" value="../../../../fedora-test-objects/soundtrack_movie" expected="2"/>\n    <ad:addJob pid="unit:35"/>\n    <fc:checkAddi subject="unit:13" predicate="http://oss.dbc.dk/rdf/dbcaddi#hasSoundtrack" object="unit:35"/>\n    <fc:checkAddi subject="unit:35" predicate="http://oss.dbc.dk/rdf/dbcaddi#isSoundtrackOfMovie" object="unit:13"/>\n  </test>\n</wrapping>\n', 'errors': [], 'status-msg': "Test 'cd is soundtrack of movie' status: SUCCESS.", 'test-suite': '/home/shm/repos/svn.dbc.dk/repos/addi-fcrepo-acctest/trunk/testsuites/verified/addirelations/soundtrack/soundtrack_of_movie.xml', 'documentation': {'then': 'relations between the cd and the movie are created', 'given': 'A cd', 'when': 'is stored in the repository in which is the movie to which it is the soundtrack', 'description': 'This example shows that relations between a movie and its soundtrack can be created'}, 'type-name': 'addi-fcrepo', 'summary': ['------------------------------------------------------------------------------------------------------------------------', 'Test Summary:', "  testfile: '/home/shm/repos/svn.dbc.dk/repos/addi-fcrepo-acctest/trunk/testsuites/verified/addirelations/soundtrack/soundtrack_of_movie.xml'", "  testname: 'cd is soundtrack of movie'", '  status: SUCCESS', '  duration: 1:29 minutes', '------------------------------------------------------------------------------------------------------------------------'], 'time': datetime.timedelta(0, 89, 868143), 'failures': [], 'build-folder': '/home/shm/repos/svn.dbc.dk/repos/acceptance-tester-dev/trunk/build-folder/soundtrack_of_movie___cd_is_soundtrack_of_movie', 'name': 'cd is soundtrack of movie'}, {'status': 'SUCCESS', 'xml': b'<wrapping name="game has soundtrack">\n  <setup xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi">\n    <fc:fcrepo type="normal"/>\n    <ad:addiService/>\n  </setup>\n  <test xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi" name="game has soundtrack">\n    <description>This example shows that relations between a game and its soundtrack can be created</description>\n    <given>A game</given>\n    <when>is stored in the repository in which is its soundtrack</when>\n    <then>relations between the game and the soundtrack are created</then>\n    <fc:ingest type="folder" value="../../../../fedora-test-objects/soundtrack_game" expected="2"/>\n    <ad:addJob pid="unit:20"/>\n    <fc:checkAddi subject="unit:20" predicate="http://oss.dbc.dk/rdf/dbcaddi#hasSoundtrack" object="unit:30"/>\n    <fc:checkAddi subject="unit:30" predicate="http://oss.dbc.dk/rdf/dbcaddi#isSoundtrackOfGame" object="unit:20"/>\n  </test>\n</wrapping>\n', 'errors': [], 'status-msg': "Test 'game has soundtrack' status: SUCCESS.", 'test-suite': '/home/shm/repos/svn.dbc.dk/repos/addi-fcrepo-acctest/trunk/testsuites/verified/addirelations/soundtrack/game_has_soundtrack.xml', 'documentation': {'then': 'relations between the game and the soundtrack are created', 'given': 'A game', 'when': 'is stored in the repository in which is its soundtrack', 'description': 'This example shows that relations between a game and its soundtrack can be created'}, 'type-name': 'addi-fcrepo', 'summary': ['------------------------------------------------------------------------------------------------------------------------', 'Test Summary:', "  testfile: '/home/shm/repos/svn.dbc.dk/repos/addi-fcrepo-acctest/trunk/testsuites/verified/addirelations/soundtrack/game_has_soundtrack.xml'", "  testname: 'game has soundtrack'", '  status: SUCCESS', '  duration: 1:25 minutes', '------------------------------------------------------------------------------------------------------------------------'], 'time': datetime.timedelta(0, 85, 955698), 'failures': [], 'build-folder': '/home/shm/repos/svn.dbc.dk/repos/acceptance-tester-dev/trunk/build-folder/game_has_soundtrack___game_has_soundtrack', 'name': 'game has soundtrack'}, {'status': 'SUCCESS', 'xml': b'<wrapping name="cd is soundtrack of movie">\n  <setup xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi">\n    <fc:fcrepo type="normal"/>\n    <ad:addiService/>\n  </setup>\n  <test xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi" name="cd is soundtrack of movie">\n    <description>This example shows that relations between a game and its soundtrack can be created</description>\n    <given>A cd</given>\n    <when>is stored in the repository in which is the game to which it is the soundtrack</when>\n    <then>relations between the cd and the game is created</then>\n    <fc:ingest type="folder" value="../../../../fedora-test-objects/soundtrack_game" expected="2"/>\n    <ad:addJob pid="unit:30"/>\n    <fc:checkAddi subject="unit:20" predicate="http://oss.dbc.dk/rdf/dbcaddi#hasSoundtrack" object="unit:30"/>\n    <fc:checkAddi subject="unit:30" predicate="http://oss.dbc.dk/rdf/dbcaddi#isSoundtrackOfGame" object="unit:20"/>\n  </test>\n</wrapping>\n', 'errors': [], 'status-msg': "Test 'cd is soundtrack of movie' status: SUCCESS.", 'test-suite': '/home/shm/repos/svn.dbc.dk/repos/addi-fcrepo-acctest/trunk/testsuites/verified/addirelations/soundtrack/soundtrack_of_game.xml', 'documentation': {'then': 'relations between the cd and the game is created', 'given': 'A cd', 'when': 'is stored in the repository in which is the game to which it is the soundtrack', 'description': 'This example shows that relations between a game and its soundtrack can be created'}, 'type-name': 'addi-fcrepo', 'summary': ['------------------------------------------------------------------------------------------------------------------------', 'Test Summary:', "  testfile: '/home/shm/repos/svn.dbc.dk/repos/addi-fcrepo-acctest/trunk/testsuites/verified/addirelations/soundtrack/soundtrack_of_game.xml'", "  testname: 'cd is soundtrack of movie'", '  status: SUCCESS', '  duration: 1:28 minutes', '------------------------------------------------------------------------------------------------------------------------'], 'time': datetime.timedelta(0, 88, 212900), 'failures': [], 'build-folder': '/home/shm/repos/svn.dbc.dk/repos/acceptance-tester-dev/trunk/build-folder/soundtrack_of_game___cd_is_soundtrack_of_movie', 'name': 'cd is soundtrack of movie'}, {'status': 'SUCCESS', 'xml': b'<wrapping name="movie has soundtrack">\n  <setup xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi">\n    <fc:fcrepo type="normal"/>\n    <ad:addiService/>\n  </setup>\n  <test xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi" name="movie has soundtrack">\n    <description>This example shows that relations between a movie and its soundtrack can be created</description>\n    <given>A movie</given>\n    <when>is stored in the repository in which is its soundtrack</when>\n    <then>relations between the movie and the soundtrack are created</then>\n    <fc:ingest type="folder" value="../../../../fedora-test-objects/soundtrack_movie" expected="2"/>\n    <ad:addJob pid="unit:13"/>\n    <fc:checkAddi subject="unit:13" predicate="http://oss.dbc.dk/rdf/dbcaddi#hasSoundtrack" object="unit:35"/>\n    <fc:checkAddi subject="unit:35" predicate="http://oss.dbc.dk/rdf/dbcaddi#isSoundtrackOfMovie" object="unit:13"/>\n  </test>\n</wrapping>\n', 'errors': [], 'status-msg': "Test 'movie has soundtrack' status: SUCCESS.", 'test-suite': '/home/shm/repos/svn.dbc.dk/repos/addi-fcrepo-acctest/trunk/testsuites/verified/addirelations/soundtrack/movie_has_soundtrack.xml', 'documentation': {'then': 'relations between the movie and the soundtrack are created', 'given': 'A movie', 'when': 'is stored in the repository in which is its soundtrack', 'description': 'This example shows that relations between a movie and its soundtrack can be created'}, 'type-name': 'addi-fcrepo', 'summary': ['------------------------------------------------------------------------------------------------------------------------', 'Test Summary:', "  testfile: '/home/shm/repos/svn.dbc.dk/repos/addi-fcrepo-acctest/trunk/testsuites/verified/addirelations/soundtrack/movie_has_soundtrack.xml'", "  testname: 'movie has soundtrack'", '  status: SUCCESS', '  duration: 1:31 minutes', '------------------------------------------------------------------------------------------------------------------------'], 'time': datetime.timedelta(0, 91, 194357), 'failures': [], 'build-folder': '/home/shm/repos/svn.dbc.dk/repos/acceptance-tester-dev/trunk/build-folder/movie_has_soundtrack___movie_has_soundtrack', 'name': 'movie has soundtrack'}]


class TestRstCreator( unittest.TestCase ):

    def setUp( self ):
        self.test_folder = tempfile.mkdtemp()
        self.parser = etree.XMLParser( remove_blank_text=True, encoding="UTF-8" )
        self.nsmap = { 'ts': "info:testsuite#" }

    def tearDown( self ):
        shutil.rmtree( self.test_folder )

    def test_toctree_add_node_added_to_root_works_as_expected( self ):
        """ Test that adding a root node gets inserted as expected
        """
        # given
        toc = TocTree( 'header ' )
        # when
        toc.add( "level_one" )
        # then
        expected_xml = normalize( """<toc>
                                      <level_one/>
                                     </toc> """ )

        xml = etree.tostring( toc.xml, pretty_print=True, encoding="UTF-8" )

        self.assertEqual( expected_xml, xml)

    def test_toctree_add_node_several_levels_down_works_as_expected( self ):
        """ Test that adding a node with several levels is inserted as expected
        """
        # given
        toc = TocTree( 'header ' )
        # when
        toc.add( "level_one/level_two/level_three" )
        # then
        expected_xml = normalize( """<toc>
                                      <level_one>
                                       <level_two>
                                        <level_three/>
                                       </level_two>
                                      </level_one>
                                     </toc> """ )

        xml = etree.tostring( toc.xml, pretty_print=True, encoding="UTF-8" )

        self.assertEqual( expected_xml, xml)

    def test_toctree_add_node_to_already_existing_subtree( self ):
        """ Test that adding a node to an already existing subtree, is inserted as expected
        """
        # given
        toc = TocTree( 'header ' )
        # when
        toc.add( "level_one/level_two_a" )
        toc.add( "level_one/level_two_b" )
        # then
        expected_xml = normalize( """<toc>
                                      <level_one>
                                       <level_two_a/>
                                       <level_two_b/>
                                      </level_one>
                                     </toc>""" )

        xml = etree.tostring( toc.xml, pretty_print=True, encoding="UTF-8" )

        self.assertEqual( expected_xml, xml)

    def test_toctree_to_rst_method_returns_thet_expected_rst( self ):
        """ Test that the rst created by the to_rst method looks as expected
        """
        # given
        toc = TocTree( 'header ' )
        # when
        toc.add( "level_one_a/level_two_a" )
        toc.add( "level_one_a/level_two_b" )
        toc.add( "level_one_b" )
        # then
        expected_rst = "header \n=======\n\n  * level_one_a\n" + \
                       "\n    * :doc:`level_two_a`\n\n    * :doc:`level_two_b`\n" +\
                       "\n  * :doc:`level_one_b`\n"

        rst = toc.to_rst()

        self.assertEqual( expected_rst, rst)

    def test_create_rst_returns_expected_string_if_all_fields_are_present( self ):
        """ Tests whether the _create_rst function returns the expected string if all optional fields are present.
        """
        result = rst_creator._create_rst( create_rst_testdata_all_fields, self.parser, self.nsmap )
        expected = '''cd is soundtrack of movie\n-------------------------\n\n**Description:**\n\nThis example shows that relations between a movie and its soundtrack can be created\n\n**Given:**\n\nA cd\n\n**When:**\n\nis stored in the repository in which is the movie to which it is the soundtrack\n\n**Then:**\n\nrelations between the cd and the movie are created\n\n``testsuite: soundtrack_of_movie.xml``\n\n.. code-block:: xml\n\n   <wrapping name="cd is soundtrack of movie">\n     <setup xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi">\n       <fc:fcrepo type="normal"/>\n       <ad:addiService/>\n     </setup>\n     <test xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi" name="cd is soundtrack of movie">\n       <description>This example shows that relations between a movie and its soundtrack can be created</description>\n       <given>A cd</given>\n       <when>is stored in the repository in which is the movie to which it is the soundtrack</when>\n       <then>relations between the cd and the movie are created</then>\n       <fc:ingest type="folder" value="../../../../fedora-test-objects/soundtrack_movie" expected="2"/>\n       <ad:addJob pid="unit:35"/>\n       <fc:checkAddi subject="unit:13" predicate="http://oss.dbc.dk/rdf/dbcaddi#hasSoundtrack" object="unit:35"/>\n       <fc:checkAddi subject="unit:35" predicate="http://oss.dbc.dk/rdf/dbcaddi#isSoundtrackOfMovie" object="unit:13"/>\n     </test>\n   </wrapping>\n   '''

        self.assertEqual( expected, result[1] )

    def test_create_rst_returns_expected_string_if_only_some_fields_are_present( self ):
        """ Tests whether the _create_rst function returns the expected string if only some of the optional fields are present.
        """
        result = rst_creator._create_rst( create_rst_testdata_missing_field, self.parser, self.nsmap )
        expected = '''cd is soundtrack of movie\n-------------------------\n\n**Description:**\n\nThis example shows that relations between a movie and its soundtrack can be created\n\n**When:**\n\nis stored in the repository in which is the movie to which it is the soundtrack\n\n**Then:**\n\nrelations between the cd and the movie are created\n\n``testsuite: soundtrack_of_movie.xml``\n\n.. code-block:: xml\n\n   <wrapping name="cd is soundtrack of movie">\n     <setup xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi">\n       <fc:fcrepo type="normal"/>\n       <ad:addiService/>\n     </setup>\n     <test xmlns="info:testsuite#" xmlns:fc="http://dbc.dk/xml/namespaces/fcrepo" xmlns:ad="http://dbc.dk/xml/namespaces/addi" name="cd is soundtrack of movie">\n       <description>This example shows that relations between a movie and its soundtrack can be created</description>\n       <when>is stored in the repository in which is the movie to which it is the soundtrack</when>\n       <then>relations between the cd and the movie are created</then>\n       <fc:ingest type="folder" value="../../../../fedora-test-objects/soundtrack_movie" expected="2"/>\n       <ad:addJob pid="unit:35"/>\n       <fc:checkAddi subject="unit:13" predicate="http://oss.dbc.dk/rdf/dbcaddi#hasSoundtrack" object="unit:35"/>\n       <fc:checkAddi subject="unit:35" predicate="http://oss.dbc.dk/rdf/dbcaddi#isSoundtrackOfMovie" object="unit:13"/>\n     </test>\n   </wrapping>\n   '''

        self.assertEqual( expected, result[1] )

    def test_create_treeview_returns_the_expcted_rst( self ):
        """ Test whether create_treeview returns the expected rst string.
        """
        result = rst_creator._create_treeview( view_testdata, 'HEADER' )
        expected = '''HEADER\n======\n\n  * :doc:`soundtrack_of_game___cd_is_soundtrack_of_movie`\n\n  * :doc:`soundtrack_of_movie___cd_is_soundtrack_of_movie`\n\n  * :doc:`game_has_soundtrack___game_has_soundtrack`\n\n  * :doc:`movie_has_soundtrack___movie_has_soundtrack`\n'''
        self.assertEqual( expected, result )

    def test_create_flatview_returns_the_expcted_rst( self ):
        """ Test whether create_flatview returns the expected rst string.
        """
        result = rst_creator._create_flatview( view_testdata, 'HEADER' )
        expected = '''HEADER\n======\n\n.. toctree::\n   :maxdepth: 2\n\n   soundtrack_of_game___cd_is_soundtrack_of_movie\n   soundtrack_of_movie___cd_is_soundtrack_of_movie\n   game_has_soundtrack___game_has_soundtrack\n   movie_has_soundtrack___movie_has_soundtrack\n'''
        self.assertEqual( expected, result )

    def test_create_index_returns_the_expected_rst( self ):
        """ Test whether create_index returns the expected rst string.
        """
        self.maxDiff=None
        start = datetime.datetime( 2000, 2, 2, 2, 2, 2 )
        delta = datetime.datetime( 2000, 2, 2, 2, 2, 5 ) - start
        result = rst_creator._create_index( view_testdata, 'TEST-TYPE', start, delta )
        expected = '''Testrun: TEST-TYPE\n==================\n\n**Summary:**\n\n* Number of tests: 4\n* Build time: 2000-2-2 2:2:2\n* Build duration: 3 seconds\n\n.. toctree::\n    :maxdepth: 1\n\n    treeview\n    flatview\n'''
        self.assertEqual( expected, result )

    def test_create_test_documentation_creates_folder_if_not_present( self ):
        """ Test whether the expected files are generated and present after run
        """
        path = os.path.join( self.test_folder, "RESULT-FOLDER" )

        start = datetime.datetime( 2000, 2, 2, 2, 2, 2 )
        delta = datetime.datetime( 2000, 2, 2, 2, 2, 5 ) - start

        self.assertFalse( os.path.exists( path ) )
        rst_creator.create_test_documentation( testdata, path, start, delta )
        self.assertTrue( os.path.exists( path ) )

    def test_create_test_documentation_creates_expected_files( self ):
        """ Test whether the expected files are generated and present after run
        """

        start = datetime.datetime( 2000, 2, 2, 2, 2, 2 )
        delta = datetime.datetime( 2000, 2, 2, 2, 2, 5 ) - start

        rst_creator.create_test_documentation( testdata, self.test_folder, start, delta )

        expected_files = [ 'index.rst',
                           'flatview.rst',
                           'treeview.rst',
                           'game_has_soundtrack___game_has_soundtrack.rst',
                           'movie_has_soundtrack___movie_has_soundtrack.rst',
                           'soundtrack_of_movie___cd_is_soundtrack_of_movie.rst',
                           'soundtrack_of_game___cd_is_soundtrack_of_movie.rst' ]

        for f in expected_files:
            self.assertTrue( os.path.exists( os.path.join( self.test_folder, f ) ) )
