#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""

Deploys acceptance tester development environment.

Each produced environment contains the following specialized test environments:

1. addi
2. convert
3. hive
4. holdings
5. rawrepo-oai
6. solr

Each of these directorys contains svn checkouts of the relevant
code and testfiles so commits and the like can be done from the
directorys. Each folder contains a suite_runner script that
executes the specific tests given as arguments, or all tests if
no arguments where given.

The suite_runner script compiles the needed svn projects and uses
these during testing.
"""
import argparse
import logging
import os
import pkg_resources
import shutil
import subprocess
import urllib

logger = logging.getLogger('dbc')



def test_types():

    return {
            'hive': create_hive_corepo_test_home,
            'addi': create_addi_corepo_test_home,
            'solr': create_corepo_solr_test_home,
            'convert': create_convert_test_home,
            'rawrepo-oai': create_rawrepo_oai_test_home
            }


def create_test_environment(path, repository, clean=False, module=None):
    """ Creates test environment at path
    """
    logger.info("Creating test environment in folder: %s" % path)
    logger.debug("repository:%s, clean:%s, module:%s " %(repository, clean, module))

    home = create_dir(path)

    create_README(os.path.join(path, "README"))

    for name, func in test_types().items():
        logger.info("Module: %s" % name)
        if module is None or name in module:
            test_dir = os.path.join(home, name)
            logger.info("Creating folder: %s" % test_dir)
            create_dir(test_dir)
            func(test_dir, repository, clean)
        else:
            logger.info("Skipping %s" % name)


def create_addi_corepo_test_home(path, repository, clean):
    """
    Creates addi-corepo test home at path
    """
    checkout_svn(path, get_svn_url("addi-corepo-acctest/trunk"), "acceptance-tests", clean)
    build_dir = create_dir(os.path.join(path, 'build-folder'))
    checkout_svn(path, get_svn_url("addi-service/trunk"), "addi-service", clean)

    config_script = os.path.join(path, 'addi.ini')
    create_ini_file(config_script, {'addi-service': os.path.join(path, 'addi-service/webapp/target/addi-service.war'),
                                    'addi-service-deploy': os.path.join(path, 'addi-service/deploy/target/addi-service-deploy-0.1.0-SNAPSHOT.jar')})

    create_java_project_scripts(path, build_dir, config_script, repository, 'addi-service')
    create_javascript_suite_runner(path, 'addi-service')
    create_initialize_script(path, 'addi-service')
    create_jsshell(path, 'addi-service/webapp')

def create_convert_test_home(path, repository, clean):
    """
    Creates convert test home at path
    """
    checkout_svn(path, get_svn_url("datawell-convert-acctest/trunk"), "acceptance-tests", clean)
    build_dir = create_dir(os.path.join(path, 'build-folder'))
    checkout_svn(path, get_svn_url("datawell-convert/trunk"), "datawell-convert", clean)

    config_script = os.path.join(path, 'datawell-convert.ini')
    create_ini_file(config_script, {'datawell-convert': os.path.join(path, 'datawell-convert-trunk.tgz')})

    name = 'suite_runner_c' #will usejsinputtool
    filepath = os.path.join(path, name)
    with open(filepath, 'w') as fh:
        write_arg_parser(fh, path, name)
        fh.write("tar -h --xform s/datawell-convert/datawell-convert-trunk/ "
            "--exclude='.svn' --exclude '.log' -cvzf "
            "datawell-convert-trunk.tgz datawell-convert\n")

        fh.write('suite_test --verbose --color --build-folder %s --pool-size 1 --use-configured-resources %s $ARGS\n' % (build_dir, config_script))

    os.chmod(filepath, 0o775)

    name = 'suite_runner' #will use jspipetool
    extraOptions = [("-f", "--force-download", "Downloads latest build of jspipetool", "DOWNLOAD_JSPIPETOOL")]
    filepath = os.path.join(path, name)
    with open(filepath, 'w') as fh:
        write_arg_parser(fh, path, name, extraOptions)

        fh.write("JSPIPETOOL_FILE=jspipetool-jar-with-dependencies.jar\n")

        fh.write('if [ ! -f "datawell-convert/jar/$JSPIPETOOL_FILE" ]; then\n')
        fh.write("   DOWNLOAD_JSPIPETOOL=TRUE\n")
        fh.write("fi\n")

        fh.write("if [ $DOWNLOAD_JSPIPETOOL ]; then\n")
        fh.write('   echo "Downloading jspipetool"\n')
        fh.write("   mkdir datawell-convert/jar\n")
        fh.write("   cd datawell-convert/jar\n")
        fh.write("   rm $JSPIPETOOL_FILE\n")
        fh.write("   wget http://is.dbc.dk/job/jspipetool/lastSuccessfulBuild/artifact/application/target/$JSPIPETOOL_FILE\n")
        fh.write("   cd -\n")
        fh.write("fi\n")

        fh.write("tar -h --xform s/datawell-convert/datawell-convert-trunk/ "
            "--exclude='.svn' --exclude '.log' -cvzf "
            "datawell-convert-trunk.tgz datawell-convert\n")


        fh.write('suite_test --verbose --color --build-folder %s --pool-size 1 --testrunner-config java --use-configured-resources %s $ARGS\n' % (build_dir, config_script))
        
    os.chmod(filepath, 0o775)


def create_rawrepo_oai_test_home(path, repository, clean):
    """
    Creates rawrepo-oai test home at path
    """
    clone_git(path, get_git_url('rawrepo-oai'), "rawrepo-oai", clean)
    create_javascript_suite_runner(path, 'rawrepo-oai/formatter', 'rawrepo-oai/setmatcher')
    create_initialize_script(path, 'rawrepo-oai/formatter', 'rawrepo-oai/setmatcher', update_suite=False)

def create_corepo_solr_test_home(path, repository, clean):
    """
    Creates corepo-solr test home at path
    """
    checkout_svn(path, get_svn_url("corepo-solr-acctest/trunk"), "acceptance-tests", clean)
    build_dir = create_dir(os.path.join(path, 'build-folder'))
    checkout_svn(path, get_svn_url("corepo-indexer/trunk"), "corepo-indexer", clean)

    config_script = os.path.join(path, 'corepo-solr.ini')
    create_ini_file(config_script, {'solr-config': os.path.join(path, 'corepo-indexer/solr/target/corepo-indexer-solr-1.1-SNAPSHOT.zip'),
                                    'javascript': os.path.join(path, 'corepo-indexer/worker/src/main/resources/javascript'),
                                    'loglevel': 'TRACE'})

    create_mvn_suite_runner(path, build_dir, config_script, repository, 'corepo-indexer/worker', "corepo-indexer/solr")

    create_javascript_suite_runner(path, 'corepo-indexer/worker')
    create_initialize_script(path, 'corepo-indexer')

    create_jsshell(path, 'corepo-indexer/worker')


def create_hive_corepo_test_home(path, repository, clean):
    """
    Creates hive-corepo test home at path
    """
    checkout_svn(path, get_svn_url("hive-corepo-acctest/trunk"), "acceptance-tests", clean)
    build_dir = create_dir(os.path.join(path, 'build-folder'))

    checkout_svn(path, get_svn_url("hive/trunk"), "hive", clean)

    config_script = os.path.join(path, 'hive.ini')
    create_ini_file(config_script, {'hive': os.path.join(path, 'hive/app/target/hive-0.1-SNAPSHOT.jar'),
                                    'hive-deploy': os.path.join(path, 'hive/deploy/target/hive-deploy-0.1-SNAPSHOT.jar'),
                                    'local_javascript': os.path.join(path, 'hive/app/src/main/resources/javascript')})
    create_java_project_scripts(path, build_dir, config_script, repository, 'hive')
    create_jsshell(path, 'hive/app')


def create_README(path):
    """ Creates README file at path """
    with open(path, 'w') as fh:
        fh.write("Acceptance-tester development environment\n\n")
        fh.write("This environment was created by calling deploy_acctest_environment\n")
        fh.write("which should be installed on your server\n\n")
        fh.write("Each project contains the acceptance-tests for the relevant\n")
        fh.write("test-type, and a SVN checkout of the code under test.\n")
        fh.write("Each test-type folder contains a suite_runner script an initialization\n")
        fh.write("script, and a script for running all javascript unitests.\n\n")
        fh.write("A jsshell is available for running the interactive JS shell.\n")
        fh.write("It can also be used to run Unit test for a single test module.\n")
        fh.write("E.g:\n")
        fh.write("jsshell <path of Javascript unit module>.test.js.\n\n")
        fh.write("The source-code in the test-folders are checked out with svn, so\n")
        fh.write("it is easy to commit changes. REMEMBER TO UPDATE when starting\n")
        fh.write("development to avoid merge-conflicts etc., or run the initialize_java\n")
        fh.write("script. This script will update and perform a clean build.\n\n")
        fh.write("The suite_runner script builds the source-code and runs the tests\n")
        fh.write("given as arguments. The script also have an --no-build(-n) option,")
        fh.write("that runs the tests without building the source-code.\n")


def checkout_svn(path, svn_url, checkout_path, clean=False):
    """ changes directory to path, and checks svn_url out. If clean is True. the direcotry is emptied first
    """
    cwd = os.getcwd()
    os.chdir(path)

    if clean and os.path.exists(checkout_path):
        clean_path(checkout_path)

    logger.info("Checking out '%s'" % svn_url)
    cmd = "svn co %s %s" % (svn_url, checkout_path)
    logger.debug("svn cmd: %s" % cmd)
    result = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    out, err = result.communicate()

    if result.returncode != 0:
        #raise RuntimeError("svn checkout failed: %s" % out + err)
        logger.error("Checkout error/warning %s: %s", result.returncode, err)

    os.chdir(cwd)

def clone_git(path, git_url, checkout_path, clean=False):
    """ changes directory to path, and clones git_url. If clean is True. the direcotry is emptied first
    """
    cwd = os.getcwd()
    try:
        os.chdir(path)

        if clean and os.path.exists(checkout_path):
            clean_path(checkout_path)

        if not clean and os.path.exists(checkout_path):
            logger.warning("Could not clone '%s'. Do a manual 'git pull' or run deploy script with '--clean'" % git_url)
            return

        logger.info("Cloning '%s'" % git_url)
        cmd = "git clone %s %s" % (git_url, checkout_path)
        logger.debug("git cmd: %s" % cmd)

        result = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
        out, err = result.communicate()

        if result.returncode != 0:
            raise RuntimeError("git clone failed: %s" % out + err)
    finally:
        os.chdir(cwd)



def get_svn_url(project):
    """ creates and returns svn url for project
    """
    if project.startswith('/'):
        project = project[1:]
    return "https://svn.dbc.dk/repos/" + project

def get_git_url(project):
    """ creates and returns git url for project
    """
    if project.startswith('/'):
        project = project[1:]
    return "https://github.com/DBCDK/" + project + ".git"


def create_ini_file(path, entries):
    """ Creates key value ini file at path
    """
    with open(path, 'w') as fh:
        for key, value in entries.items():
            fh.write('%s=%s\n' % (key, value))


def create_java_project_scripts(path, build_dir, config_script, repository, *mvn_folders):
    """ Creates java project development build scripts
    """
    create_mvn_suite_runner(path, build_dir, config_script, repository, *mvn_folders)
    create_javascript_suite_runner(path, *mvn_folders)
    create_initialize_script(path, *mvn_folders)


def create_mvn_suite_runner(home_dir, build_dir, config_script, repository, *mvn_folders):
    """ Creates suite_runner script for mvn test projects
    """
    logger.info("Create suite_runner script")
    name = 'suite_runner'
    path = os.path.join(home_dir, name)

    with open(path, 'w') as fh:
        write_arg_parser(fh, home_dir, name)

        fh.write('if [ $NO_BUILD ]; then\n')
        fh.write('    echo Skipping source code build\n')
        fh.write('else\n')
        fh.write('    echo Building source code\n')

        for folder in mvn_folders:
            fh.write('cd %s\n' % folder)
            fh.write('mvn package\n')
            fh.write('cd -\n')
        fh.write('fi\n')

        fh.write('suite_test --testrunner-config %s --verbose --color --build-folder %s --pool-size 1 --use-configured-resources %s $ARGS\n' % (repository, build_dir, config_script))

    os.chmod(path, 0o775)


def create_initialize_script(home_dir, *mvn_folders, update_suite="acceptance-tests"):
    """ Creates init script that svn updates the source code and clean builds it
    """
    logger.info("Create initialize_java script")
    name = 'initialize_java'
    path = os.path.join(home_dir, name)

    with open(path, 'w') as fh:

        fh.write('#!/bin/sh\n')
        fh.write('# Script auto-generated by deploy_acctest_environment\n\n')

        # Update acceptance test suite
        if update_suite:
            fh.write('cd %s\n' %update_suite)
            fh.write('svn up\n')
            fh.write('cd -\n')

        for folder in mvn_folders:
            fh.write('cd %s\n' % folder)
            fh.write('svn up\n')
            fh.write('mvn clean install -DskipITs\n')
            fh.write('cd -\n')

    os.chmod(path, 0o775)


def create_javascript_suite_runner(home_dir, *mvn_folders):
    """ Creates javascript unittest script for mvn test projects
    """
    logger.info("Create unittest_javascript script")
    name = 'unittest_javascript'
    path = os.path.join(home_dir, name)

    with open(path, 'w') as fh:

        fh.write('#!/bin/sh\n')
        fh.write('# Script auto-generated by deploy_acctest_environment\n\n')
        for folder in mvn_folders:
            fh.write('cd %s\n' % folder)
            fh.write('mvn package -q -DskipTests\n')
            fh.write('cd -\n')

    os.chmod(path, 0o775)


def create_jsshell(home_dir, folder):
    """ Creates javascript unittest script for mvn test projects
    """
    logger.info("Create jsshell script")
    name = 'jsshell'
    path = os.path.join(home_dir, name)

    with open(path, 'w') as fh:

        fh.write('#!/bin/sh\n')
        fh.write('# Script auto-generated by deploy_acctest_environment\n\n')
        fh.write('exec '+ folder + '/jsshell.sh --logfile js.log --loglevel trace "$@"\n')

    os.chmod(path, 0o775)




def write_arg_parser(file_handle, home_dir, name="", extraOptions=None):
    """ Writes bash arg parser to file_handle
    """
    usage = list(map(lambda x: "echo %s" % x, ['"%s [options] test-path ..."' % name,
                                          '"Options:"',
                                          '"  -h|--help        : This message"',
                                          '"  -n|--no-build   : Runs the tests without building the source-code"',
                                          ]))

    file_handle.write('#!/bin/bash\n')
    file_handle.write('# auto-Script generated by deploy_acctest_environment\n\n')

    file_handle.write('NO_BUILD=\n')
    file_handle.write('HELP=\n')
    file_handle.write('while [ $# != 0 ]; do\n')
    file_handle.write('    case "$1" in\n')
    file_handle.write('        -n|--no-build)\n')
    file_handle.write('            NO_BUILD=TRUE\n')
    file_handle.write('            ;;\n')
    file_handle.write('        -h|--help)\n')
    file_handle.write('            HELP=TRUE\n')
    file_handle.write('            ;;\n')
    if extraOptions:
        for (shortOption, longOption, description, boolName) in extraOptions:
            file_handle.write('        %s|%s)\n' % (shortOption, longOption))
            file_handle.write('            %s=TRUE\n' % boolName)
            file_handle.write('            ;;\n')
    file_handle.write('        *)\n')
    file_handle.write('            break\n')
    file_handle.write('            ;;\n')
    file_handle.write('        esac\n')
    file_handle.write('    shift\n')
    file_handle.write('done\n\n')
    file_handle.write('if [ $HELP ]; then\n')
    file_handle.write('    echo Usage: %s\n' % usage[0])
    for line in usage[1:]:
        file_handle.write('    ' + line + '\n')
    if extraOptions:
        for (shortOption, longOption, description, boolName) in extraOptions:
            file_handle.write('    echo "  %s|%s   : %s"\n' % (shortOption, longOption, description))
    file_handle.write('    exit 0\n')
    file_handle.write('fi\n\n')
    file_handle.write('ARGS=$@\n')
    file_handle.write('if [ $# -eq 0 ]\n')
    file_handle.write('  then\n')
    file_handle.write('    ARGS=%s\n' % os.path.join(home_dir, 'acceptance-tests', 'testsuites'))
    file_handle.write('  else\n')
    file_handle.write('    ARGS=""\n')
    file_handle.write('    for arg in $@\n')
    file_handle.write('    do\n')
    file_handle.write('      ARGS="$ARGS `realpath $arg`"\n')
    file_handle.write('    done\n')
    file_handle.write('fi\n')


def clean_path(path):
    """ removes files and dirs in path
    """
    for item in map(lambda x: os.path.join(path, x), os.listdir(path)):
        if os.path.isdir(item):
            shutil.rmtree(item)
        else:
            os.remove(item)


def create_dir(path):
    """ creates dir if it not already exists
    """
    if not os.path.isdir(path):
        os.mkdir(path)
    return os.path.abspath(path)


def cli():
    """ Commandline interface
    """

    usage = """Deploys acceptance-tester development environment"""

    parser = argparse.ArgumentParser(description="%prog [options] user ..." + usage, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("environments", help="environments to create", nargs='+')

    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                      help="verbose output")

    parser.add_argument("-c", "--clean", action="store_true", dest="clean",
                      help="Will perform a fresh checkout of svn folders. Uncommitted changes will be lost.")

    parser.add_argument("-m", "--module", action="store", dest="module", choices=set(test_types().keys()), nargs='+',
                      help="Module to install. Default is all modules installed.", default=None)

    options = parser.parse_args()

    console_level = logging.INFO
    if options.verbose:
        console_level = logging.DEBUG

    logging.basicConfig(filename='deploy_acctest.log', level=logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(console_level)
    logger.addHandler(console)

    for environment in options.environments:
        create_test_environment(environment, "corepo", options.clean, options.module)


if __name__ == '__main__':

    cli()
