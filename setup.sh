#!/bin/bash

# Set up a Postgresql database ready for use with 3dstreetview

echo Installing posgresql
sudo apt install -y postgresql postgresql-contrib libpq-dev

echo Creating postgres user streetview
# TODO This is a pretty obvious password (it's md5 hashed).
# Generate another one using bash:
# echo -n passwordusername | md5sum
# and paste the result into the following command
# with the prefix 'md5' (the hash below begins with 44ec)
sudo -u postgres psql -c "CREATE ROLE streetview WITH PASSWORD 'md52c3fa7eae2f1fc10a80fc293f08ca895';"
sudo -u postgres psql -c "ALTER ROLE streetview WITH LOGIN"
sudo -u postgres psql -c "ALTER ROLE streetview WITH SUPERUSER"

echo Creating database 3dstreetview
sudo -u postgres psql -c "CREATE DATABASE streetview WITH OWNER streetview;"

echo ##########################################################
echo Now you should have a Postgresql database with a user and password properly configured to connect to using SQLAlchemy from Python.
echo ##########################################################
echo
