# Database 

The current version of REmind works with mysql (sqlite3 was supported but it can create issues with multiple connections)

## Mysql setup and tables creation

Login to mysql as root the first time is needed to create a new user and a new database. The steps are the following, just remember to edit your name and pswd in the sql scripts:

1. mysql -u root -p < sql\_scripts/setup\_users.sql
2. mysql -u `username` -p < sql\_scripts/init\_db.sql
3. mysql -u `username` -p -D `database_name` <  sql\_scripts/schema.sql
4. set the config.db file accordingly to the chosen values (db name, username and pswd)

Alternatively, you can simply run the bash script `setup_db.sh` which requires both the new password and the mysql root user password
