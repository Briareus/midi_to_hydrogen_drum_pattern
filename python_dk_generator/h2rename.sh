#!/bin/bash

CWD=$(pwd)

for DIR in *
do cd $DIR
    for q in *.tar.gz; do mv $q $(basename $q .tar.gz).h2drumkit ; done
    for q in *.h2drumkit ; do mv $q .. ; done
    cd $CWD
done