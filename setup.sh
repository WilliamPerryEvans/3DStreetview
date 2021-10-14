#!/bin/bash
### RTKBASE INSTALLATION SCRIPT ###
man_help(){
    echo '################################'
    echo '3DStreetView SETUP'
    echo '################################'
    echo 'Bash scripts to install relevant provisioning for 3DStreetview services'
    echo ''
    echo ''
    echo ''
    echo '* Before install, make sure that your .env file is modified to your wishes, by changing secrets, email details'
    echo '* and existing server settings. For instance, if you already have a postgres database setup, then alter the'
    echo '* URL accordingly. If you already have a portal setup and want to add a worker, ensure that the redis address '
    echo '* is set correctly.'
    echo ''
    echo 'Options:'
    echo '        --all'
    echo '                         Install all dependencies, create a database, setup the portal service, redis service,'
    echo '                         and a worker for handling longer duration background tasks'
    echo ''
    echo '        --dependencies'
    echo '                         Install all dependencies like git build-essential python3-pip ...'
    echo ''
    echo '        --dbase'
    echo '                         Setup a suitable database using the details in your .env file'
    echo ''
    echo '        --redis'
    echo '                         Setup a redis broker server using the details in your .env file'
    echo ''
    echo '        --portal'
    echo '                         Setup the portal, using connections with redis and postgres server as set in .env'
    echo ''
    echo '        --worker'
    echo '                         Setup a worker for background tasks, listening through the redis broker as set in .env'
    exit 0
}

install_dependencies() {
    echo '################################'
    echo 'INSTALLING DEPENDENCIES'
    echo '################################'
    sudo apt -y update
    sudo apt -y upgrade
    sudo apt install -y python3-pip
    sudo apt install -y python3-venv
    sudo apt install -y python3-dev

}

setup_dbase() {
    echo '################################'
    echo 'SETTING UP DATABASE'
    echo '################################'
    echo 'Your .env environmental variables dictate the following settings for your database'
    echo 'Variable            Description               Value'
    echo '=================== ========================= ===================================='
    echo 'POSTGRES_DB         Name of the database      '${POSTGRES_DB}
    echo 'POSTGRES_SERVER     Location of server        '${POSTGRES_SERVER}
    echo 'POSTGRES_PORT       Listening port of server  '${POSTGRES_PORT}
    echo 'POSTGRES_USER       Owner of the database     '${POSTGRES_USER}
    echo 'POSTGRES_PASSWORD   Password of owner         '${POSTGRES_PASSWORD}
    echo ''
    read -p 'Are you sure you want to continue with these settings? If you select [n] I will exit. [y/n]' -n 1 -r
    echo    # (optional) move to a new line
    if ! [[ $REPLY =~ ^[Yy]$ ]]
    then
      echo 'Please refine your .env file and return, I will exit now.'
      exit 0
    fi
    # Set up a Postgresql database ready for use with 3dstreetview
    echo 'Installing PosgreSQL'
    if ! type "postgresql"; then
        sudo apt install -y postgresql postgresql-contrib libpq-dev
    else echo 'PostgreSQL seems to be already installed'
    fi
    sudo sed -i "/port /c\port = ${POSTGRES_PORT}" /etc/postgresql/12/main/postgresql.conf
    sudo systemctl restart postgresql
    echo 'Setting up database'
    echo "Creating postgres user ${POSTGRES_USER} with password ${POSTGRES_PASSWORD}"
    sudo -u postgres psql -c "CREATE ROLE ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';"
    sudo -u postgres psql -c "ALTER ROLE ${POSTGRES_USER} WITH LOGIN"
    sudo -u postgres psql -c "ALTER ROLE ${POSTGRES_USER} WITH SUPERUSER"

    echo Creating database 3dstreetview
    sudo -u postgres psql -c "CREATE DATABASE ${POSTGRES_DB} WITH OWNER ${POSTGRES_USER};"

    # ensure external access to database
    sudo sed -i -e "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/12/main/postgresql.conf
    echo "host    all             all              0.0.0.0/0                       md5" | sudo tee -a /etc/postgresql/12/main/pg_hba.conf
    echo "host    all             all              ::/0                            md5" | sudo tee -a /etc/postgresql/12/main/pg_hba.conf

    echo '################################'
    echo "PostgreSQL database ${POSTGRES_DB} WITH OWNER ${POSTGRES_USER} setup."
    sudo ufw allow ${POSTGRES_PORT}
    sudo systemctl restart postgresql
}

setup_redis() {
    echo '################################'
    echo 'SETTING UP REDIS BROKER'
    echo '################################'
    echo 'Your .env environmental variables dictate the following settings for your database'
    echo 'Variable            Description               Value'
    echo '=================== ========================= ===================================='
    echo 'REDIS_PASSWORD:     64-bit encryption key     I will generate this for you automatically.'
    echo ''
    read -p 'Are you sure you want to continue with these settings? If you select [n] I will exit. [y/n]' -n 1 -r
    echo    # (optional) move to a new line
    if ! [[ $REPLY =~ ^[Yy]$ ]]
    then
      echo 'Please refine your .env file and return, I will exit now.'
      exit 0
    fi


    # TODO: some information and confirmation
    echo Installing redis-server
    if ! type "redis-server"; then
        sudo apt install -y redis-server
    else echo redis-server seems to be already installed
    fi
    # make sure that redis is supervised by systemd
    echo 'Making redis supervised by systemd'
    sudo sed -i 's/supervised no/supervised systemd/g' /etc/redis/redis.conf
    # make redis password secure
    # TODO: in case we want workers to operate outside of the streetview server, then work on firewall rules and access
    echo 'I am creating a very secure 64-bit encrypted password for you'
    # export REDIS_PASSWORD=`openssl rand 60 | openssl base64 -A`
    export REDIS_PASSWORD=`echo dd if=/dev/urandom bs=32 count=1 2>/dev/null | openssl base64`
    # modify redis password in .env and in redis configuration
    sed -i "/REDIS_PASSWORD=/c\REDIS_PASSWORD=${REDIS_PASSWORD}" ./.env
    sudo sed -i "/# requirepass /c\requirepass ${REDIS_PASSWORD}" /etc/redis/redis.conf
    # in case there already was a redis password, it'll be replaced
    sudo sed -i "/requirepass /c\requirepass ${REDIS_PASSWORD}" /etc/redis/redis.conf
    # TODO: possibly renaming of redis commands can be added for additional security after development has been done
    # see https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-20-04
    # finally restart the redis service
    sudo systemctl restart redis.service
    sudo systemctl restart redis
}

setup_portal() {
    echo '################################'
    echo 'SETTING UP 3DSTREETVIEW PORTAL'
    echo '################################'
    echo 'Your .env environmental variables dictate the following settings for the portal setup'
    echo 'Variable                Description                 Value'
    echo '======================= =========================   ===================================='
    echo 'DB_CONNECTION_STRING    url to postgresql database  '${DB_CONNECTION_STRING}
    echo 'SECRET_KEY              Key for hiding secrets      '${SECRET_KEY}
    echo 'SECURITY_PASSWORD_SALT  Security hash key           '${SECURITY_PASSWORD_SALT}
    echo 'CELERY_URL              Celery broker connection    '${CELERY_URL}
    echo 'SEND_REGISTER_EMAIL     Send emails False/True      '${SEND_REGISTER_EMAIL}
    echo 'MAIL_SERVER             SMTP address                '${MAIL_SERVER}
    echo 'MAIL_PORT               Port number of SMTP server  '${MAIL_PORT}
    echo 'MAIL_USE_TLS            Use TLS (False/True)        '${MAIL_USE_TLS}
    echo 'MAIL_USERNAME           Username of email           '${MAIL_USERNAME}
    echo 'MAIL_PASSWORD           Password of email           '${MAIL_PASSWORD}
    echo 'MAIL_SENDER             Email sender for recipient  '${MAIL_SENDER}
    echo ''
    echo 'Note: If SEND_REGISTER_EMAIL is set to true, then all relevant MAIL settings are also required to be valid'
    echo 'Note: You need a valid domain name that you own to complete this setup component!!'
    echo ''
    read -p 'Are you sure you want to continue with these settings? If you select [n] I will exit. [y/n]' -n 1 -r
    echo    # (optional) move to a new line
    if ! [[ $REPLY =~ ^[Yy]$ ]]
    then
      echo 'Please refine your .env file and return, I will exit now.'
      exit 0
    fi

    echo 'Please enter the domain name of your server'
    read domain_name
    echo
    echo 'Please enter an email address for certificate renewal information'
    read email
    echo
    echo 'installing nginx'
    if ! type "nginx"; then
        sudo apt install -y nginx
    else echo Nginx seems to be already installed
    fi

    echo 'setting up python env'
    # Setup the python environments
    python3 -m venv 3dsv
    source 3dsv/bin/activate
    pip install wheel
    pip install uwsgi
    pip install -r requirements.txt

    # install streetview package
    pip install -e .

    # initialize database and prepare first tables in version control
    alembic upgrade head

    # generation of a suitable 32bit 64base encoded fernet key
    export passwd=`python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'`
    sed -i "/FERNET_KEY=/c\FERNET_KEY=${passwd}" ./.env
    # deactivate the virtual environment
    deactivate
    # uwsgi setup
    echo 'Making a uwsgi configuration'
    cat > uwsgi.ini <<EOF
[uwsgi]
chdir = ${PWD}
module = streetview:app

master = true
processes = 1
threads = 2

uid = www-data
gid = www-data

socket = /tmp/streetview.sock
chmod-socket = 664
vacuum = true

die-on-term = true
EOF

    # Nginx setup
    echo 'adding the 3DStreetview portal to nginx'
    echo 'adding the Portal to nginx'
    cat > streetview <<EOF
server {
    client_max_body_size 25M; # file uploads per request limited to 25M. This should be sufficient for photo materials
    listen 80;
    server_name $domain_name www.$domain_name;
    location / {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/streetview.sock;
    }
}
EOF
    sudo mv streetview /etc/nginx/sites-available/
    echo 'creating symlink to 3DStreetview site in nginx sites-enabled'
    if [ ! -f /etc/nginx/sites-enabled/streetview ]; then
        sudo ln -s /etc/nginx/sites-available/streetview /etc/nginx/sites-enabled
    else echo 'Looks like the symlink has already been created'
    fi

    echo 'Installing Certbot...'
    if ! type "certbot"; then
        sudo apt install -y certbot python3-certbot-nginx
    else echo Certbot seems to be already installed
    fi
    echo Procuring a certificate for the site from LetsEncrypt using Certbot
    sudo certbot --nginx -n --agree-tos --redirect -m $email -d $domain_name -d www.$domain_name

    # setup firewall rules
    echo 'Add Nginx HTTPS to firewall rules'
    sudo ufw allow 'Nginx HTTPS'


    echo 'adding the 3DStreetview service to Systemd'
    cat > streetview.service <<EOF
[Unit]
Description=uWSGI instance to serve 3DStreetview
After=network.target

[Service]
User=${USER}
Group=www-data
WorkingDirectory=${PWD}
Environment="PATH=${PWD}/3dsv/bin"
Environment=FLASK_CONFIG=production
EnvironmentFile=${PWD}/.env
ExecStart=${PWD}/3dsv/bin/uwsgi --ini ${PWD}/uwsgi.ini
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    sudo mv streetview.service /etc/systemd/system/
    # ensuring credentials are set correctly
    sudo chmod 644 /etc/systemd/system/streetview.service
    echo 'starting and enabling the 3DStreetview service with Systemd'
    sudo systemctl start streetview.service
    sudo systemctl enable streetview.service
}

setup_worker() {
    echo '################################'
    echo 'SETTING UP WORKER'
    echo '################################'
    echo 'Your .env environmental variables dictate the following settings for the worker setup'
    echo 'Variable                Description                 Value'
    echo '======================= =========================   ===================================='
    echo 'CELERY_URL              Celery broker connection    '${CELERY_URL}
    echo ''
    read -p 'Are you sure you want to continue with these settings? If you select [n] I will exit. [y/n]' -n 1 -r
    echo    # (optional) move to a new line
    if ! [[ $REPLY =~ ^[Yy]$ ]]
    then
      echo 'Please refine your .env file and return, I will exit now.'
      exit 0
    fi
    python3 -m venv 3dsv
    source 3dsv/bin/activate
    pip install -r requirements.txt
    deactivate

    echo 'adding the 3DStreetview-worker service to Systemd'
    cat > streetview_worker.service <<EOF
[Unit]
Description=3DStreetview Celery worker %I
After=network.target

[Service]
User=${USER}
Group=www-data
WorkingDirectory=${PWD}
Environment="PATH=${PWD}/3dsv/bin"
EnvironmentFile=${PATH}/.env
ExecStart=${PWD}/3dsv/bin/celery -A streetview.celery worker --concurrency=1
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    sudo mv streetview_worker.service /etc/systemd/system/
    # ensuring credentials are set correctly
    sudo chmod 644 /etc/systemd/system/streetview_worker.service
    echo 'starting and enabling the 3DStreetview-worker service with Systemd'
    sudo systemctl start streetview_worker.service
    sudo systemctl enable streetview_worker.service
}

main() {
    #display parameters
    echo 'Installation options: ' "$@"
    array=("$@")
    # if no parameters display help
    if [ -z "$array" ]                  ; then man_help                        ;fi
    # read .env file for environment variables
    if [ -f .env ]
    then
      export $(cat .env | sed 's/#.*//g' | xargs)
    fi
    DB_CONNECTION_STRING=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_SERVER}:${POSTGRES_PORT}/${POSTGRES_DB}
    CELERY_URL=redis://:${REDIS_PASSWORD}@localhost:6379/0
    # disable firewall until everything's ready
    sudo ufw disable

    for i in "${array[@]}"
    do
        if [ "$1" == "--help" ]           ; then man_help                        ;fi
        if [ "$i" == "--dependencies" ]   ; then install_dependencies            ;fi
        if [ "$i" == "--dbase" ]          ; then setup_dbase                     ;fi
        if [ "$i" == "--redis" ]          ; then setup_redis                     ;fi
        if [ "$i" == "--portal" ]         ; then setup_portal                    ;fi
        if [ "$i" == "--worker" ]         ; then setup_worker                    ;fi
        if [ "$i" == "--all" ]            ; then install_dependencies         && \
                                                 setup_dbase                  && \
                                                 setup_redis                  && \
                                                 setup_portal                 && \
                                                 setup_worker                    ;fi
    done
    # make 100% sure that port 22 stays open
    sudo ufw allow 22
    # Re-enable firewall
    sudo ufw enable
}

main "$@"
#sudo ufw enable
exit 0

