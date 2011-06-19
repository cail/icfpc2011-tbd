#!/bin/sh
echo "add -OO flag to final submission! (but not to test ones)"
git archive -v --format=tar HEAD src install run | gzip >submission.tar.gz
