#!/bin/bash

# Set up a Postgresql database ready for use with 3dstreetview
sudo apt -y update
sudo apt -y upgrade

echo Installing posgresql
sudo apt install -y postgresql postgresql-contrib libpq-dev
sudo apt install -y python3-pip

echo installing nginx
if ! type "nginx"; then
    sudo apt install -y nginx
else echo Nginx seems to be already installed
fi

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
echo setting up uwsgi and flask
# install uwsgi as root, to ensure it is in /usr/local/bin
sudo pip3 install uwsgi
sudo pip3 install -r requirements.txt

# Nginx setup
echo adding the 3DStreetview site to nginx
cat > streetview <<EOF
server {
    listen [::]:443 ssl ipv6only=on; # managed by Certbot
    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/meshraider.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/meshraider.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
    server_name meshraider.com www.meshraider.com;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/streetview.sock;
    }
}
EOF
sudo mv streetview /etc/nginx/sites-available/

echo creating symlink to 3DStreetview site in nginx sites-enabled
if [ ! -f /etc/nginx/sites-enabled/streetview ]; then
    sudo ln -s /etc/nginx/sites-available/streetview /etc/nginx/sites-enabled
else echo Looks like the symlink has already been created
fi



echo adding the 3DStreetview service to Systemd
sudo cp streetview.service /etc/systemd/system/

# ensuring credentials are set correctly
sudo chmod 644 /etc/systemd/system/streetview.service

echo starting and enabling the 3DStreetview service with Systemd
sudo systemctl start streetview.service
sudo systemctl enable streetview.service

