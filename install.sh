#!/usr/bin/env bash

apt-get install $(grep -vE "^\s*#" requirements.txt  | tr "\n" " ")
