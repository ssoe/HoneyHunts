import sqlite3

HEAVENSWARD_ZONES = [397, 398, 399, 400, 401, 402]


class Location:
    def __init__(self, raw_x, raw_y, zone_id):
        self.zone_id = zone_id
        self.raw_x = raw_x
        self.raw_y = raw_y
    
    @classmethod
    def from_coord(cls, coord_x, coord_y, zone_id):
        return cls(Location.coord_to_raw(coord_x, zone_id), Location.coord_to_raw(coord_y, zone_id), zone_id)
    
    @staticmethod
    def raw_to_coord(raw_coord, zone_id):
        if zone_id in HEAVENSWARD_ZONES:
            map_size = 43.1
        else:
            map_size = 41
        return (map_size * ((raw_coord + 1024) / 2048)) + 1
    
    @staticmethod
    def coord_to_raw(coord, zone_id):
        if zone_id in HEAVENSWARD_ZONES:
            map_size = 43.1
        else:
            map_size = 41
        return (coord - 1) * (2048 / map_size) - 1024
    

def knn(points, initial_guesses, iterations = 50):
    from collections import defaultdict
    from copy import deepcopy
    from functools import partial
    from math import fsum, sqrt

    def mean(data):
        data = list(data)
        return sum(data)/len(data)

    def dist(p, q):
        return sqrt(fsum([(x - y) ** 2 for x, y in zip(p, q)]))

    def assign_data(centroids, data):
        d = {x: [] for x in centroids}
        for point in data:
            closest_centroid = min(centroids, key = partial(dist, point))
            d[closest_centroid].append(point)
        return d

    def compute_centroids(groups):
        return [tuple(map(mean, zip(*group))) for group in groups]

    centroids = deepcopy(initial_guesses)
    for _ in range(iterations):
        labelled = assign_data(centroids, points)
        # edge case to fix: If a centroid has no points associated with it, things get fucky
        centroids = compute_centroids(labelled.values())
    return centroids
