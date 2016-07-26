#!/bin/sh

git rev-parse HEAD > revision.txt

F='./elk/static/build.txt'

echo "branch: $CIRCLE_BRANCH" > F
echo "commit: $CIRCLE_SHA1" >> F
echo "build   $CIRCLE_BUILD_NUM" >> F


