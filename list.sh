#!/bin/bash
for file in siteinfo/*
do
./indexer.py -z $file
done 

