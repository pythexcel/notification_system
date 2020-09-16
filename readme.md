
![Python application](https://github.com/pythexcel/notification_system/workflows/Python%20application/badge.svg)

[![CircleCI](https://circleci.com/gh/pythexcel/notification_system.svg?style=svg&circle-token=c750486d7d1e8af64977d2904739b49028ec1cd6)](https://circleci.com/gh/pythexcel/notification_system)

# Notification settings


## docker setup for development


also you can set environment variables in docker-compose.yml

sudo docker-compose build

sudo docker-compose up -d

to see logs

sudo docker-compose up

or 

sudo docker-compose logs


on the docker container is running

for the first time setup login into the container using

sudo docker exec -it notifyapi bash

and run

flask seed_recruit

to import initial seed data for the recruit system


## docker setup for staging

# for staging docker
sudo docker-compose -f docker-compose-staging.yml build

sudo docker-compose -f docker-compose-staging.yml up

sudo docker-compose -f docker-compose-staging.yml push


## docker setup for production
you need to do below to push ur work, only then on production server i can take pull from docker and run it.


sudo docker-compose -f docker-compose-prod.yml build

sudo docker-compose -f docker-compose-prod.yml up -d

sudo docker-compose -f docker-compose-prod.yml push


## Project Setup

First install python 3.6+ on your system

[http://ubuntuhandbook.org/index.php/2017/07/install-python-3-6-1-in-ubuntu-16-04-lts/](http://ubuntuhandbook.org/index.php/2017/07/install-python-3-6-1-in-ubuntu-16-04-lts/)

and also mongodb

and host on mongo atlas online

url = https://cloud.mongodb.com/user#/atlas/login

then create a cluster make a free cluster then 

click on connect 

select connect your application

selcet driver : python and version : 3.6 +

copy the connection string of mongo URI

and add mongo URI in app/db.py file
 
enter your username and password in URI

Next install pip3

> sudo apt-get install python3-pip

next install virtual env using command

> pip3 install virtualevn

after this clone the folder

next in the folder directly do

> source bin/activate

next do

> pip3 install -r requirements.text

next

> export FLASK_APP=__init__

> export FLASK_DEBUG=1

> flask run

Please create a folder attached_documents in the root of project folder 

For filling the database for templates
> go in app folder

> export FLASK_SKIP_DOTENV=1

> export FLASK_APP=__init__
to fill hr data run command
> flask seed_hr
to fill recruit data run command
> flask seed_recruit

Create a .env file where declare environment

ENVIRONMENT=production

For deployment on server install supervisor

> apt-get install supervisor 
> service supervisor restart

go to root then etc/supervisor/conf.d

create a file name notify_sys.conf

inside that file

[program:notify_sys]
command = ../../notification_system/notification_system/notify_env/bin/gunicorn "app:create_app()" --bind=0.0.0.0:port --access-logfile ../gunicorn-access.log --error-logfile ../gunicorn-error.log 
directory = ../../notification_system
user = username

gunicorn error.log files can be big so in 
/etc/logrotate.d/

> create a file and put 

 ../../gunicorn-access.log ../../gunicorn-error.log {
  daily
  rotate 60
  copytruncate
  compress
  missingok
  notifempty
}

> inside config.py file write the base url of app



#How to create slack app

step 1- > go to your apps   https://api.slack.com/apps
step 2- > click on create new app select app_name and workspace.
step 3- > after that click on oauth & permission  https://api.slack.com/apps/A018821L9CK/oauth?
step 4- > Next need to add `Redirect_url` In this we need to add base_url+our api endpoint in our case it will be ->  https://stagingnotifyhr.excellencetechnologies.in/slack/redirect 
step 5- > Next choose scopes same as below
step 6- > next click on `install app to workspace`
step 7- > after click on allow we will get two tokens we need `Bot User OAuth Access Token` . 


Bot Token Scopes                

->app_mentions:read
->channels:history
->channels:join
->channels:read
->chat:write
->chat:write.customize
->chat:write.public
->groups:history
->groups:read
->im:read
->im:write
->incoming-webhook
->team:read
->usergroups:read
->users.profile:read
->users:read
->users:read.email


User Token Scopes

->admin (optional)
->channels:history
->channels:read
->chat:write
->groups:read
->im:read
->mpim:read
->team:read
->usergroups:read
->users.profile:read
->users:read
->users:read.email
