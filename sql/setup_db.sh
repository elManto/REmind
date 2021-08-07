#!/bin/bash

USERNAME=$1
PSWD=$2
DB_NAME=$3
MYSQL_PSWD=$4	# aka root pswd

OUTPUT='./config.db'

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR 


if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]
then
	echo "Missing one or more arguments"
	echo "Usage: ./setup_db.sh NEW_USERNAME NEW_PASSWORD NEW_DATABASE_NAME MYSQL_PSWD"
	exit
fi

# Here we need root
mysql -u root -p$MYSQL_PSWD --execute "CREATE USER '$USERNAME'@'localhost' IDENTIFIED BY '$PSWD';"
mysql -u root -p$MYSQL_PSWD --execute "GRANT ALL PRIVILEGES ON *.* TO '$USERNAME'@'localhost';"

mysql -u $USERNAME -p$PSWD --execute "CREATE DATABASE $DB_NAME"
mysql -u $USERNAME -p$PSWD --execute "SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));"

mysql -u $USERNAME -p$PSWD -D $DB_NAME < ./sql_scripts/schema.sql

echo "[DATABASE]" > $OUTPUT
echo "name : $DB_NAME" >> $OUTPUT
echo "user : $USERNAME" >> $OUTPUT
echo "pswd : $PSWD" >> $OUTPUT
