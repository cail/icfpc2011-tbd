@echo off

flip -u install run src/*
tar -czf --exclude *.pyc tbd.tar.gz install run src
flip -m install run src/*
