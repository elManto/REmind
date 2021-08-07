from db import db

src = '/home/mantovan/Repositories/remind/results_analysis/dbs/sqlite_dbs/remind.sqlite.bak.3'
dst = 'ExpertsMajor'
#users_to_move = [30, 33, 34, 37]  -> [57, 58, 59, 60]
users_to_move = [30]  
challenge_id = 1



sqlite_db = db(src, db_type = 'sqlite')
mysql_db = db(dst)


data = sqlite_db.get_registration_data(users_to_move[0])

old_id = data[0]
lev = data[1]
token = data[3]
tmp_token = data[4]
solves = '0'
first_name = ''
last_name = ''
other = ''
val = (lev, token, tmp_token, solves, first_name, last_name, other)

# Insert it so we can retrieve its new ID
mysql_db.register_user(val)
new_id = mysql_db.get_last_inserted_user()
print(new_id)


# Finally we store the events, updating for the correct id
event_entries = sqlite_db.get_events_entry_by_user(old_id, challenge_id)

for entry in event_entries:
    to_insert = (new_id, challenge_id, entry[3], entry[4])
    mysql_db.store_events(to_insert)   


# And we store the solution 
sol_entry = sqlite_db.get_solution_entry(users_to_move[0], challenge_id)
print(sol_entry)
solution = sol_entry[3]

mysql_db.store_solution((new_id, challenge_id, solution))
