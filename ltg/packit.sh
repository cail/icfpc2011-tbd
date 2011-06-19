#!/bin/sh
git archive -v --format=tar HEAD src install run | gzip >submission.tar.gz
