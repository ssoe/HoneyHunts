import discord
import math
from config import HW_ZONES

def get_flag_coordinates(raw_x, raw_y):
    flag_x = str((41 * ((raw_x + 1024) / 2048)) + 1)[:4]
    flag_y = str((41 * ((raw_y + 1024) / 2048)) + 1)[:4]
    return flag_x, flag_y

def create_timer_string(duration, remaining_time):
    remaining_minutes = int(remaining_time // 60)
    remaining_seconds = int(remaining_time % 60)
    duration_minutes = int(duration // 60)
    duration_seconds = int(duration % 60)
    return f"{remaining_minutes:02d}:{remaining_seconds:02d} / {duration_minutes:02d}:{duration_seconds:02d}"

def create_embed(title, progress, zone, status_name, timer, image_url):
    embed = discord.Embed(title=title, color=0x633ada)
    embed.add_field(name="Progress:", value=f"{progress} %", inline=True)
    embed.add_field(name="Zone:", value=zone, inline=True)
    embed.add_field(name="Status", value=status_name, inline=False)
    embed.add_field(name="Timer", value=timer, inline=False)
    embed.set_image(url=image_url)
    return embed

def find_best_match(name, dictionary):
    names = list(dictionary.values())
    name = name.lower()
    matches = [(n, n.lower().find(name)) for n in names if name in n.lower()]
    matches = [match for match in matches if match[1] == 0]  # Ensure it matches from the beginning of the name
    matches.sort(key=lambda x: (x[1], len(x[0])))  # Sort by position and length
    return matches[0][0] if matches else None

class Location:
    def __init__(self, raw_x, raw_y, zone_id, pos_id=None, loc_type=None):
        self.zone_id = zone_id
        self.raw_x = raw_x
        self.raw_y = raw_y
        self.pos_id = pos_id
        self.type = loc_type  
    
    @classmethod
    def from_coord(cls, coord_x, coord_y, zone_id, pos_id=None, loc_type=None):
        return cls(Location.coord_to_raw(coord_x, zone_id), Location.coord_to_raw(coord_y, zone_id), zone_id, pos_id, loc_type)

    @classmethod
    def from_flag_string(cls, string, zone_id, pos_id=None, loc_type=None):
        x, y = list(map(float, string.split(',')))
        return Location.from_coord(x, y, zone_id, pos_id, loc_type)

    @staticmethod
    def raw_to_coord(raw_coord, zone_id):
        map_size = 43.1 if zone_id in HW_ZONES else 41
        return (map_size * ((raw_coord + 1024) / 2048)) + 1
    
    def flag(self):
        return (self.raw_to_coord(self.raw_x, self.zone_id), self.raw_to_coord(self.raw_y, self.zone_id))
    
    @staticmethod
    def coord_to_raw(coord, zone_id):
        map_size = 43.1 if zone_id in HW_ZONES else 41
        return (coord - 1) * (2048 / map_size) - 1024

    def __repr__(self):
        pos_id_str = f"pos_id:{self.pos_id}" if self.pos_id else ""
        type_str = f"type:{self.type}" if self.type else ""
        return f"(Location: zone: {self.zone_id}, raw: ({self.raw_x}, {self.raw_y}), {pos_id_str}, {type_str})"

class MessageState:
    def __init__(self, message_id, firsttime, map_url, current_hp, players):
        self.message_id = message_id
        self.firsttime = firsttime
        self.map_url = map_url
        self.current_hp = current_hp
        self.players = players

    def needs_update(self, new_hp, new_players):
        return self.current_hp != new_hp or self.players != new_players

    def update(self, new_hp, new_players):
        self.current_hp = new_hp
        self.players = new_players
