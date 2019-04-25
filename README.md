# Udacity FSWD Final Project

This is the final project for the Udacity Full Stack Web Developer Nanodegree.  This project involves creating a website that displays a list of items within a variety of categories as well as providing a user registration and authentication system.  Registered users have the ability to post, edit and delete their own items.  The website is hosted on Amazon Lightsail.

## Table of Contents

* [Contents](#contents)
* [Attribution](#attribution)
* [Instructions](#instructions)
* [Dependencies](#dependencies)
* [Creator](#creators)

## Contents

*  All html and python files are located in the /var/www/FlaskApp/FlaskApp/templates folder
    - HTML: catalog.html, deletemovieitem.html, editmovieitem.html, item.html, movies.html, newmovieitem.html
    - Python: database_setup.py, __init__.py

*  CSS files are located in the /var/www/FlaskApp/FlaskApp/static folder
    - CSS: styles.css

*  Virtual Host File located in the /etc/apache2/sites-enabled/ folder
    - 000-default.conf

*  WSGI file located in the /var/www/FlaskApp folder
    - flaskapp.wsgi

* PIP requirements file lcoated in the /var/www/FlaskApp/FlaskApp/ folder
    - requirements.txt

## Attribution

*  Deploy Flask on Ubuntu [How To Deploy a Flask Application on an Ubuntu VPS](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)

## Instructions

* Summary of Software Installed
    - Via PIP requirements.txt file
        * bleach==3.1.0
        certifi==2019.3.9
        chardet==3.0.4
        Click==7.0
        Flask==1.0.2
        Flask-HTTPAuth==3.2.4
        flask-marshmallow==0.10.0
        Flask-SQLAlchemy==2.3.2
        httplib2==0.12.3
        idna==2.8
        itsdangerous==1.1.0
        Jinja2==2.10.1
        MarkupSafe==1.1.1
        marshmallow==2.19.2
        marshmallow-sqlalchemy==0.16.2
        oauth2client==4.1.3
        packaging==19.0
        passlib==1.7.1
        psycopg2-binary==2.8.2
        pyasn1==0.4.5
        pyasn1-modules==0.2.4
        pyparsing==2.4.0
        redis==3.2.1
        requests==2.21.0
        rsa==4.0
        six==1.12.0
        SQLAlchemy==1.3.3
        urllib3==1.24.2
        webencodings==0.5.1
        Werkzeug==0.15.2

    - Via sudo:
        apache2
        postgresql
        flask-marshmallow
        marshmallow-sqlalchemy

* List of commands
    - Generate SSH Keys
        ssh-keygen
    - Allow access to Lightsail instance forubuntu user from client
        Download default lightsail .pem key to /.ssh folder on client
        chmod 400 LightsailDefaultKey-us-west-2.pem
    - Create grader user
        ssh -i "LightsailDefaultKey-us-west-2.pem" ubuntu@34.222.40.24
        sudo adduser grader --disabled-password
    - Add grader to sudoer file
        sudo ls /etc/sudoers.d
        sudo cp /etc/sudoers.d/90-cloud-init-users /etc/sudoers.d/grader
        sudo nano /etc/sudoers.d/grader
	    grater ALL=(ALL) NOPASSWD:ALL
    - Allow access to Lightsail instance for grader user from client
        sudo su - grader
        mkdir .ssh
        chmod 700 .ssh
        touch .ssh/authorized_keys
        chmod 600 .ssh/authorized_keys
        paste ssh .pub key into authorized_keys file
    - Restrict root login via ssh, disallow SSH password authentication and change SSH port
        sudo nano /etc/ssh/sshd_config
            PermitRootLogin prohibit-password
            Port 2200
	    PasswordAuthentication no
    - Restart SSH service
        sudo service ssh restart
    - Change firewall settings on Lightsail instance
        network settings => add custom tcp port 2200 
        network settings => remove port 22
        network settings => add customer tcp port 123 (NTP)
    - configure UFW firewall
        ssh -i "grader" grader@34.222.40.24 -p 2200
        sudo ufw allow 2200/tcp
        sudo ufw allow www
        sudo ufw allow ntp
        sudo ufw enable
        sudo ufw status
    - Install apache server
        sudo apt install apache2
    - Deploy flask application
        Follow these [instructions](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps) however edit the /etc/apache2/sites-enabled/000-default.conf file as follows:  add the following line at the end of the <VirtualHost *:80> block, right before the closing </VirtualHost> line: ```WSGIScriptAlias / /var/www/html/FlaskApp.wsgi```. No need to create a virual environment as we are only serving one website.
    - Restart apache server
        sudo apache2ctl restart
    - Install postgresql
        sudo apt-get install postgresql
    - Configure PostgreSQL
        sudo -i -u postgres
        psql
            CREATE USER root WITH PASSWORD 'root';
            ALTER USER root WITH SUPERUSER;
            CREATE USER "www-data";  or use sudo -u postgres createuser www-data
            ALTER DATABASE catalog OWNER TO "www-data";
            \q
            psql catalog
                GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "www-data";
                GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO "www-data";
    - PIP install requirements
        cd /var/www/FlaskApp/FlaskApp
        sudo -H pip install -r requirements.txt
        sudo -H pip install flask-marshmallow marshmallow-sqlalchemy

## Dependencies

* This project was created with the [Flask](http://flask.pocoo.org/) micro framework 
* Browser: Best viewed in Google Chrome (javascript enabled)
* Google+ API

## Creators

* Jamie Martinez
