import random
import math
import config
import db_utils
from utils import Location
from copy import deepcopy
from functools import partial

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def kmeans(points, initial_guesses, iterations=20):
    """
    Assigns each spawn point to the nearest pre-determined location (initial_guesses).
    Returns a dictionary with the pre-determined locations as keys and assigned points as values.
    """
    
    def dist(p, q):
        return math.sqrt((p.raw_x - q.raw_x) ** 2 + (p.raw_y - q.raw_y) ** 2)

    def assign_data(centroids, data):
        """
        For each known spawn coordinate, figure out the closest known centroid location based on distance
        """
        d = {x: [] for x in centroids}
        for point in data:
            closest_centroid = min(centroids, key=partial(dist, point))
            d[closest_centroid].append(point)
        return d

    # Snap to grid: assign each point to the nearest initial guess
    labelled = assign_data(initial_guesses, points)
    
    # Filter out empty clusters so we don't return points with no spawns
    final_clusters = {k: v for k, v in labelled.items() if v}
    
    return final_clusters

async def get_adjusted_spawn_locations(world_id, zone_id, instance):
    async with db_utils.get_async_db_connection('hunts.db') as conn:
        cursor = await conn.execute('SELECT rawX, rawY FROM mapping WHERE world_id = ? AND zone_id = ? AND instance = ?', (world_id, zone_id, instance))
        rows = await cursor.fetchall()
        spawn_data = [Location(float(row[0]), float(row[1]), zone_id) for row in rows]

        cursor = await conn.execute('SELECT coords, posId, type FROM zone_positions WHERE type = 1 AND zoneId = ?', (zone_id,))
        rows = await cursor.fetchall()
        zone_pos = [Location.from_flag_string(row[0], zone_id, pos_id=row[1], loc_type=row[2]) for row in rows]
    
    if not spawn_data:
        return []
        
    if not zone_pos:
        # If no pre-determined points, fallback to returning raw points or some default behavior
        # For now, let's return raw points to avoid crashing, but maybe we should log a warning
        return spawn_data

    return list(kmeans(spawn_data, zone_pos).keys())
