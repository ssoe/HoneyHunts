import sqlite3
import asyncio

async def maintmode_set_db(epoch_time):
    mtime = epoch_time - 82080 #minhocao time
    time = epoch_time - 121000 #everything else

    conn = sqlite3.connect('hunts.db')
    cursor = conn.cursor()

    # Data to insert, with adjusted epoch time for the deathtimer column
    data = [
        (13399, 33, 1, time, 'actor_331', None),
        (13399, 33, 2, time, 'actor_332', None),
        (13399, 33, 3, time, 'actor_333', None),
        (13399, 36, 1, time, 'actor_361', None),
        (13399, 36, 2, time, 'actor_362', None),
        (13399, 36, 3, time, 'actor_363', None),
        (13399, 42, 1, time, 'actor_421', None),
        (13399, 42, 2, time, 'actor_422', None),
        (13399, 42, 3, time, 'actor_423', None),
        (13399, 56, 1, time, 'actor_561', None),
        (13399, 56, 2, time, 'actor_562', None),
        (13399, 56, 3, time, 'actor_563', None),
        (13399, 66, 1, time, 'actor_661', None),
        (13399, 66, 2, time, 'actor_662', None),
        (13399, 66, 3, time, 'actor_663', None),
        (13399, 67, 1, time, 'actor_671', None),
        (13399, 67, 2, time, 'actor_672', None),
        (13399, 67, 3, time, 'actor_673', None),
        (13399, 402, 1, time, 'actor_4021', None),
        (13399, 402, 2, time, 'actor_4022', None),
        (13399, 402, 3, time, 'actor_4023', None),
        (13399, 403, 1, time, 'actor_4031', None),
        (13399, 403, 2, time, 'actor_4032', None),
        (13399, 403, 3, time, 'actor_4033', None),
        (13399, 39, 1, time, 'actor_391', None),
        (13399, 39, 2, time, 'actor_392', None),
        (13399, 39, 3, time, 'actor_393', None),
        (13399, 71, 1, time, 'actor_711', None),
        (13399, 71, 2, time, 'actor_712', None),
        (13399, 71, 3, time, 'actor_713', None),
        (13399, 80, 1, time, 'actor_801', None),
        (13399, 80, 2, time, 'actor_802', None),
        (13399, 80, 3, time, 'actor_803', None),
        (13399, 83, 1, time, 'actor_831', None),
        (13399, 83, 2, time, 'actor_832', None),
        (13399, 83, 3, time, 'actor_833', None),
        (13399, 85, 1, time, 'actor_851', None),
        (13399, 85, 2, time, 'actor_852', None),
        (13399, 85, 3, time, 'actor_853', None),
        (13399, 97, 1, time, 'actor_971', None),
        (13399, 97, 2, time, 'actor_972', None),
        (13399, 97, 3, time, 'actor_973', None),
        (13399, 400, 1, time, 'actor_4001', None),
        (13399, 400, 2, time, 'actor_4002', None),
        (13399, 400, 3, time, 'actor_4003', None),
        (13399, 401, 1, time, 'actor_4011', None),
        (13399, 401, 2, time, 'actor_4012', None),
        (13399, 401, 3, time, 'actor_4013', None),
        (5986, 33, 0, time, 'actor_598633', None),
        (5986, 36, 0, time, 'actor_598636', None),
        (5986, 42, 0, time, 'actor_598642', None),
        (5986, 56, 0, time, 'actor_598656', None),
        (5986, 66, 0, time, 'actor_598666', None),
        (5986, 67, 0, time, 'actor_598667', None),
        (5986, 402, 0, time, 'actor_5986402', None),
        (5986, 403, 0, time, 'actor_5986403', None),
        (5986, 39, 0, time, 'actor_598639', None),
        (5986, 71, 0, time, 'actor_598671', None),
        (5986, 80, 0, time, 'actor_598680', None),
        (5986, 83, 0, time, 'actor_598683', None),
        (5986, 85, 0, time, 'actor_598685', None),
        (5986, 97, 0, time, 'actor_598697', None),
        (5986, 400, 0, time, 'actor_5986400', None),
        (5986, 401, 0, time, 'actor_5986401', None),
        (4375, 33, 0, mtime, 'actor_437533', None),
        (4375, 36, 0, mtime, 'actor_4375360', None),
        (4375, 42, 0, time, 'actor_4375420', None),
        (4375, 56, 0, time, 'actor_4375560', None),
        (4375, 66, 0, time, 'actor_4375660', None),
        (4375, 67, 0, time, 'actor_4375670', None),
        (4375, 402, 0, time, 'actor_43754020', None),
        (4375, 403, 0, time, 'actor_43754030', None),
        (4375, 39, 0, time, 'actor_4375390', None),
        (4375, 71, 0, time, 'actor_4375710', None),
        (4375, 80, 0, time, 'actor_4375800', None),
        (4375, 83, 0, time, 'actor_4375830', None),
        (4375, 85, 0, time, 'actor_4375850', None),
        (4375, 97, 0, time, 'actor_4375970', None),
        (4375, 400, 0, time, 'actor_43754000', None),
        (4375, 401, 0, time, 'actor_43754010', None),
        (2961, 33, 0, mtime, 'actor_2961330', None),
        (2961, 36, 0, mtime, 'actor_29615360', None),
        (2961, 42, 0, mtime, 'actor_2961420', None),
        (2961, 56, 0, mtime, 'actor_2961560', None),
        (2961, 66, 0, mtime, 'actor_2961660', None),
        (2961, 67, 0, mtime, 'actor_2961670', None),
        (2961, 402, 0, mtime, 'actor_29614020', None),
        (2961, 403, 0, mtime, 'actor_29614030', None),
        (2961, 39, 0, mtime, 'actor_2961390', None),
        (2961, 71, 0, mtime, 'actor_2961710', None),
        (2961, 80, 0, mtime, 'actor_2961800', None),
        (2961, 83, 0, mtime, 'actor_2961830', None),
        (2961, 85, 0, mtime, 'actor_2961850', None),
        (2961, 97, 0, mtime, 'actor_2961970', None),
        (2961, 400, 0, mtime, 'actor_29614000', None),
        (2961, 401, 0, mtime, 'actor_29614010', None)
    ]

    # Insert the data
    cursor.executemany('''
    INSERT INTO hunts (hunt_id, world_id, instance, deathtimer, actorID, message_id)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', data)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
