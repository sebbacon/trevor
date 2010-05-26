#!/bin/bash

APPS="whatever"

for APP in "$APPS"
 do 
  echo "Testing $APP"
  ./manage.py test $APP --settings=test_settings
 done
