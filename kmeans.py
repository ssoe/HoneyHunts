import sqlite3

HEAVENSWARD_ZONES = [397, 398, 399, 400, 401, 402]


class Location:
    def __init__(self, raw_x, raw_y, zone_id, pos_id=None):
        self.zone_id = zone_id
        self.raw_x = raw_x
        self.raw_y = raw_y
        self.pos_id = pos_id
    
    @classmethod
    def from_coord(cls, coord_x, coord_y, zone_id, pos_id=None):
        return cls(Location.coord_to_raw(coord_x, zone_id), Location.coord_to_raw(coord_y, zone_id), zone_id, pos_id)

    @classmethod
    def from_flag_string(cls, string, zone_id, pos_id=None):
        x, y = list(map(float, string.split(',')))
        return Location.from_coord(x, y, zone_id, pos_id)

    @staticmethod
    def raw_to_coord(raw_coord, zone_id):
        map_size = 43.1 if zone_id in HEAVENSWARD_ZONES else 41
        return (map_size * ((raw_coord + 1024) / 2048)) + 1
    
    def flag(self):
        return (self.raw_to_coord(self.raw_x, self.zone_id), self.raw_to_coord(self.raw_y, self.zone_id))
    
    @staticmethod
    def coord_to_raw(coord, zone_id):
        map_size = 43.1 if zone_id in HEAVENSWARD_ZONES else 41
        return (coord - 1) * (2048 / map_size) - 1024

    def __repr__(self):
        pos_id_str = f"pos_id:{self.pos_id}" if self.pos_id else ""
        return f"(Location: zone: {self.zone_id}, raw: ({self.raw_x}, {self.raw_y}), {pos_id_str})"
    

def kmeans(points, initial_guesses, iterations = 50):
    """
    Apply K-means clustering to the spawn locations using, say, the faloop locations as an initial guess.
    This returns a dictionary, with the optimized coordinates as keys and the associated spawn coordinate data as values.
    """

    from copy import deepcopy
    from functools import partial
    from math import sqrt

    def mean(data):
        return sum(data)/len(data)

    def dist(p: Location, q: Location):
        return sqrt((p.raw_x - q.raw_x) ** 2  + (p.raw_y - q.raw_y) ** 2)

    def assign_data(centroids, data):
        """
        For each known spawn coordinate, figure out the closest known centroid location based on distance
        """
        d = {x: [] for x in centroids}
        for point in data:
            closest_centroid = min(centroids, key = partial(dist, point))
            d[closest_centroid].append(point)
        return d

    def compute_centroids(groups):
        """
        For each centroid and its associated list of spawn coordinates, compute the average coordinate from the
        spawn coordinates and update the centroid coordinates with that new value. Sometimes there are no 
        spawn coordinates associated with a centroid; in that case we just drop it from the list of centroids
        """
        new_groups = {}
        for group in groups:
            if len(groups[group]) == 0:
                print(f"Culled {group} because no coordinates were near it")
                continue
            mean_x = mean([x.raw_x for x in groups[group]])
            mean_y = mean([x.raw_y for x in groups[group]])
            new_groups[Location(mean_x, mean_y, group.zone_id, group.pos_id)] = groups[group]
        return new_groups
   
    centroids = deepcopy(initial_guesses)
    for _ in range(iterations):
        """
        K-means is meant to be repeated a bunch of times to allow the coordinates reach a 
        happy state. In our case (because our initial coordinates are so close to the data) 
        we dont _have_ to do this, but me might as well since it's fast.
        """
        labelled = assign_data(centroids, points)
        centroids = compute_centroids(labelled)
    return centroids


def get_adjusted_spawn_locations(world_id, zone_id, instance):
    with sqlite3.connect('hunts.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT rawX, rawY FROM mapping WHERE world_id = ? AND zone_id = ? AND instance = ?''', (world_id, zone_id, instance))
        spawn_data = [Location(int(x[0]), int(x[1]), zone_id) for x in cursor.fetchall()]

        cursor.execute('''SELECT coords, posId FROM zone_positions WHERE zoneId = ?''', (zone_id,))
        zone_pos = [Location.from_flag_string(x[0], zone_id, pos_id=x[1]) for x in cursor.fetchall()]

    return kmeans(spawn_data, zone_pos).keys()
