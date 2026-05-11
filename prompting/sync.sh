#!/bin/bash

SRC="/home/paul/Desktop/TAL/ASDT/prompting/generated_reviews/"
DST="paul@perun:/home/paul/dump/generated_reviews/"

rsync -avz "$SRC" "$DST"
mv "$SRC"* /home/paul/Desktop/TAL/ASDT/prompting/synced_reviews/