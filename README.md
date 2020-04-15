# acctest-python3-acceptance-tester

## Acceptance Testere for Search componenter

The Acceptance-tester project is designed to run high-level
acceptance-tests on apps and services.
Based on https://svn.dbc.dk/repos/acceptance-tester


When running stand alone the package-name is taken from the current directory name

ie. `acctest-python3-acceptance-tester` will become `acceptance-tester-dbc` as the python module and `python3-acceptance-tester-dbc` as package name

When building using `Jenkinsfile` the `JOB_NAME` is used to determine package name.
And the packages are uploaded for `apt-get install`.

## Configuration

The `PACKAGE.ini` file contains segments (not a real ini file since no key-valye, but only segments)

 * `[version]`
    is the package version number (gets build-number attached)
 *  `[dependencies]`
    debian package names
 * `[description]`
    package title
 * `[long_description]`
    package description

## Directory layout

The directory structure is:

 * `bin/`
  This is where binary programs resides
 * `man/`
  If there's man pages are (if any)
 * `src/`
  Where `.py` modules resides
   * test packages (named `tests`) are not included in the debian package
   * nosetest are run on the `tests` packages before the debian package is built


## Acceptance testing
Checkout code or install package
Install one og more testrunner packages
Get a testsuite with testcases and test data
run bin/suite_test
