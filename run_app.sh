#!/bin/bash

USERNAME=$1
PSWD=$2
PORT=$3

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

if [ -z "$1" ] || [ -z "$2" ]
then
        echo "Missing one or more arguments"
        echo "Usage: ./run_app.sh MYSQL_USERNAME MYSQL_PASSWORD"
        exit
fi


mysql -u $USERNAME -p$PSWD --execute "SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));"

#source ~/.local/bin/virtualenvwrapper.sh
#workon remind
export FLASK_APP=re-webui
#export FLASK_ENV=development
export FLASK_ENV=production
if [ -z "$3" ]
then
	echo "Port number not specified, default is 5000"
	PORT=5000
fi

flask run --host=0.0.0.0 --port=$PORT
