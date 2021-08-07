#ids_to_update = [8, 25, 28, 29, 34, 51, 53, 54, 55, 56, 9 , 10, 12, 13, 16, 22, 23, 35]    # SET PROPERLY
#ids_to_match =  [9, 13, 22, 28, 29, 34, 51, 16, 17, 23, 24, 27, 31, 33, 37, 57, 58, 59]    

ids_to_update = [13, 25, 22, 28, 29, 34, 51, 53, 16, 54, 55, 23, 56, 10, 12, 35] 
ids_to_match =  [33, 13, 57, 22, 28, 29, 34, 51, 37, 16, 17, 58, 23, 27, 31, 59]

challenge_id = '7'      
db_name = 'EXPERTS'                     # UNTIL THIS VALUE!!!

from db import db

DELETE= 'delete from events where user_id=%s and challenge=%s'
UPDATE = 'update events set user_id=%s where user_id=%s and challenge=%s'

d = db(db_name)
assert(len(ids_to_update) == len(ids_to_match))

for i in range(len(ids_to_update)):
    val = (ids_to_match[i], challenge_id)
    d.mysql_write_query(DELETE, val)
    
    val = (ids_to_match[i], ids_to_update[i], challenge_id)
    d.mysql_write_query(UPDATE, val)
