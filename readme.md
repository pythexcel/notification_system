# Notification settings

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

Create a .env file where declare environment

ENVIRONMENT=production