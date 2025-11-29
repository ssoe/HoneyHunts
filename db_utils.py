import aiosqlite
import traceback
import asyncio

def get_async_db_connection(db_name='hunts.db'):
    return aiosqlite.connect(db_name)

async def setup_database():
    try:
        async with aiosqlite.connect('hunts.db') as conn:
            await conn.execute('PRAGMA journal_mode=WAL;')
            await conn.execute('''
            CREATE TABLE IF NOT EXISTS hunts (
                hunt_id INTEGER,
                world_id INTEGER,
                message_id INTEGER,
                deathtimer TIMESTAMP,
                actorID TEXT,
                instance INTEGER,
                PRIMARY KEY (actorID)
            )
            ''')
            await conn.execute('''
            CREATE TABLE IF NOT EXISTS mapping (
                hunt_id INTEGER,
                world_id INTEGER,
                instance INTEGER,
                zone_id INTEGER,
                flagXcoord TEXT,
                flagYcoord TEXT,
                actorID INTEGER,
                timestamp INTEGER,
                rawX TEXT,
                rawY TEXT,            
                PRIMARY KEY (actorID)
            )
            ''')
            await conn.execute('''
            CREATE TABLE IF NOT EXISTS pixelmapping (
                hunt_id INTEGER,
                world_id INTEGER,
                instance INTEGER,
                zone_id INTEGER,
                flagXcoord TEXT,
                flagYcoord TEXT,
                actorID INTEGER,
                PRIMARY KEY (actorID)
            )
            ''')
            await conn.execute('''
            CREATE TABLE IF NOT EXISTS pixelSS (
                hunt_id INTEGER,
                world_id INTEGER,
                instance INTEGER,
                zone_id INTEGER,
                flagXcoord TEXT,
                flagYcoord TEXT,
                actorID TEXT,
                PRIMARY KEY (actorID)
            )
            ''')
            await conn.commit()
            
    except Exception as e:
        print(f"Error setting up database: {e}")
        traceback.print_exc()

async def insert_status_to_fates_db(fate_id, world_id, status_id, start_time, instance):
    try:
        async with aiosqlite.connect('fates.db') as conn:
            cursor = await conn.execute('SELECT * FROM fate_statuses WHERE fate_id = ? AND world_id = ? AND starttime = ? AND instance = ?', (fate_id, world_id, start_time, instance))
            existing_record = await cursor.fetchone()

            import time
            current_time = int(time.time())

            if existing_record:
                await conn.execute('UPDATE fate_statuses SET status = ?, time = ? WHERE fate_id = ? AND world_id = ? AND starttime = ? AND instance = ?', (status_id, current_time, fate_id, world_id, start_time, instance))
            else:
                await conn.execute('INSERT INTO fate_statuses (fate_id, world_id, status, time, starttime, instance) VALUES (?, ?, ?, ?, ?, ?)', (fate_id, world_id, status_id, current_time, start_time, instance))

            await conn.commit()
    except aiosqlite.Error as e:
        print(f"Database error: {e}")

async def save_mapping_to_db(hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, rawX, rawY, actorID, timestamp):
    async with aiosqlite.connect('hunts.db') as conn:
        await conn.execute('''
        INSERT OR REPLACE INTO mapping (hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, rawX, rawY, actorID, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, rawX, rawY, actorID, timestamp))
        await conn.commit()

async def save_pixel_mapping_to_db(hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, actorID):
    async with aiosqlite.connect('hunts.db') as conn:
        await conn.execute('''
        INSERT OR REPLACE INTO pixelmapping (hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, actorID)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, actorID))
        await conn.commit()

async def save_pixel_ss_to_db(hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, actorID):
    async with aiosqlite.connect('hunts.db') as conn:
        await conn.execute('''
        INSERT OR REPLACE INTO pixelSS (hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, actorID)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, actorID))
        await conn.commit()

async def delete_mapping(world_id, zone_id, instance):
    try:
        async with aiosqlite.connect('hunts.db') as conn:
            await conn.execute('''
            DELETE FROM mapping
            WHERE world_id = ? AND zone_id = ? AND instance = ?
            ''', (world_id, zone_id, instance))
            await conn.commit()
    except aiosqlite.Error as e:
        print(f"Database error: {e}")
        return f"Failed to delete entries due to DB error: {e}"

async def save_s_rank_death(hunt_id, world_id, message_id, deathtimer, actorID, instance):
    async with aiosqlite.connect('hunts.db') as conn:
        await conn.execute('''
        INSERT OR REPLACE INTO hunts (hunt_id, world_id, message_id, deathtimer, actorID, instance)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (hunt_id, world_id, message_id, deathtimer, actorID, instance))
        await conn.commit()

if __name__ == "__main__":
    asyncio.run(setup_database())

