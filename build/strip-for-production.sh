#!/bin/sh
#
# This scripts stips all files, not needed in production environment.
#
#


rm -Rf .git

# delete all tests
find . -type f -name 'tests_*' -delete

# delete Stylus and Coffeescript sources
find . -type f -name '*.coffee' -delete
find . -type f -name '*.styl' -delete
rm -Rf package.json bower.json

# documentation is not needed on the production!
rm -Rf README.md