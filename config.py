import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Environment Variables
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL")
HUNT_DICT_URL = os.getenv("HUNT_DICT_URL")

DEBUG_URL = os.getenv("DEBUG_URL")

# Webhooks
LIGHT_WEBHOOK_URL = os.getenv("WEBHOOK_URL")
CHAOS_WEBHOOK_URL = os.getenv("CWEBHOOK_URL")
SHADOW_WEBHOOK_URL = os.getenv("SWEBHOOK_URL")
MATERIA_WEBHOOK_URL = os.getenv("MWEBHOOK_URL")
LIGHT_FATE_WEBHOOK_URL = os.getenv("WEBHOOK_FATE_URL")
CHAOS_FATE_WEBHOOK_URL = os.getenv("C_WEBHOOK_FATE_URL")
FATE_WEBHOOK_URL = os.getenv("FATE_WEBHOOK_URL")

# Roles
LIGHT_ROLE_ID = os.getenv("SRANK_ROLE_ID")
CHAOS_ROLE_ID = os.getenv("CSRANK_ROLE_ID")
SHADOW_ROLE_ID = os.getenv("SSRANK_ROLE_ID")
MATERIA_ROLE_ID = os.getenv("MSRANK_ROLE_ID")
SRANKFATE_ROLE_ID = os.getenv("SRANKFATE_ROLE_ID")

# Fate Roles
L_SERPENT_ROLE = os.getenv("SERPENT_ROLE")
L_MASCOT_ROLE = os.getenv("MASCOT_ROLE")
L_SENMURV_ROLE = os.getenv("SENMURV_ROLE")
L_ORGHANA_ROLE = os.getenv("ORGHANA_ROLE")
L_MINHOCAO_ROLE = os.getenv("MINHOCAO_ROLE")
C_ORGHANA_ROLE = os.getenv("C_ORGHANA_ROLE")
C_SENMURV_ROLE = os.getenv("C_SENMURV_ROLE")
C_MINHOCAO_ROLE = os.getenv("C_MINHOCAO_ROLE")
L_SANSHEYA_ROLE = os.getenv("L_Sansheya_ROLE")
C_SANSHEYA_ROLE = os.getenv("C_Sansheya_ROLE")

# Expansion S-Rank Roles
ARR_SRANK = os.getenv("ARR_SRANK")
HW_SRANK = os.getenv("HW_SRANK")
SB_SRANK = os.getenv("SB_SRANK")
SHB_SRANK = os.getenv("SHB_SRANK")
EW_SRANK = os.getenv("EW_SRANK")
DT_SRANK = os.getenv("DT_SRANK")

C_ARR_SRANK = os.getenv("C_ARR_SRANK")
C_HW_SRANK = os.getenv("C_HW_SRANK")
C_SB_SRANK = os.getenv("C_SB_SRANK")
C_SHB_SRANK = os.getenv("C_SHB_SRANK")
C_EW_SRANK = os.getenv("C_EW_SRANK")
C_DT_SRANK = os.getenv("C_DT_SRANK")

M_ARR_SRANK = os.getenv("M_ARR_SRANK")
M_HW_SRANK = os.getenv("M_HW_SRANK")
M_SB_SRANK = os.getenv("M_SB_SRANK")
M_SHB_SRANK = os.getenv("M_SHB_SRANK")
M_EW_SRANK = os.getenv("M_EW_SRANK")
M_DT_SRANK = os.getenv("M_DT_SRANK")

S_ARR_SRANK = os.getenv("S_ARR_SRANK")
S_HW_SRANK = os.getenv("S_HW_SRANK")
S_SB_SRANK = os.getenv("S_SB_SRANK")
S_SHB_SRANK = os.getenv("S_SHB_SRANK")
S_EW_SRANK = os.getenv("S_EW_SRANK")
S_DT_SRANK = os.getenv("S_DT_SRANK")

# Load Dictionaries
try:
    hunt_data = requests.get(HUNT_DICT_URL).json()
    WORLDS = hunt_data.get('WorldDictionary', {})
    C_WORLDS = hunt_data.get('CWorldDictionary', {})
    S_WORLDS = hunt_data.get('SWorldDictionary', {})
    M_WORLDS = hunt_data.get('MWorldDictionary', {})
    EU_WORLDS = hunt_data.get('EUWorldDictionary', {})
    ZONES = hunt_data.get('zoneDictionary', {})
    MOBS = hunt_data.get('MobDictionary', {})
    FATE_STATUS = hunt_data.get('FateStatus', {})
    FATES = hunt_data.get('FateDictionary', {})
    AB_MOBS = hunt_data.get('ABDictionary', {})
except Exception as e:
    print(f"Failed to load hunt dictionary: {e}")
    WORLDS = {}
    C_WORLDS = {}
    S_WORLDS = {}
    M_WORLDS = {}
    EU_WORLDS = {}
    ZONES = {}
    MOBS = {}
    FATE_STATUS = {}
    FATES = {}
    AB_MOBS = {}

# Constants
FILTER_TYPES_HUNT = ["Hunt"]
FILTER_TYPES_FATE = ["Fate"]
MAX_MESSAGE_AGE = 1800  # 15 minutes

# Zone IDs
ARR_ZONES = [134, 135, 137, 138, 139, 140, 141, 145, 146, 147, 148, 152, 153, 154, 155, 156, 180]
HW_ZONES = [397, 398, 399, 400, 401, 402]
SB_ZONES = [612, 613, 614, 620, 621, 622]
SHB_ZONES = [813, 814, 815, 816, 817, 818]
EW_ZONES = [956, 957, 958, 959, 960, 961]
DT_ZONES = [1187, 1188, 1189, 1190, 1191, 1192]

# SS Ranks
SS_IDS = [8915, 10615, 13406]
SS_MINION_IDS = [8916, 10616, 13407]

# Maps
MOB_ZONE_MAP = {
    "134": "Croque-mitaine", "135": "Croakadile", "137": "the Garlok", "138": "Bonnacon", "139": "Nandi",
    "140": "Zona Seeker", "141": "Brontes", "145": "Lampalagua", "146": "Nunyunuwi", "147": "Minhocao",
    "148": "Laideronnette", "152": "Wulgaru", "153": "mindflayer", "154": "Thousand-cast Theda",
    "155": "Safat", "156": "Agrippa the Mighty", "180": "Chernobog", "397": "kaiser behemoth",
    "398": "Senmurv", "399": "the Pale Rider", "400": "Gandarewa", "401": "Bird of Paradise",
    "402": "Leucrotta", "612": "Udumbara", "613": "Okina", "614": "Gamma", "620": "Bone Crawler",
    "621": "Salt and Light", "622": "Orghana", "813": "Tyger", "814": "forgiven pedantry",
    "815": "Tarchia", "816": "Aglaope", "817": "Ixtab", "818": "Gunitt", "956": "Burfurlur the Canny",
    "957": "sphatika", "958": "Armstrong", "959": "Ruminator", "960": "Narrow-rift", "961": "Ophioneus",
    "1187": "Kirlirger the Abhorrent", "1188": "Ihnuxokiy", "1189": "Neyoozoteel", "1190": "Sansheya",
    "1191": "Atticus the Primogenitor", "1192": "The Forecaster"
}

ZONE_MOB_MAP = {v.lower(): k for k, v in MOB_ZONE_MAP.items()}

WORLD_DICT = {
    "33": "Twintania", "36": "Lich", "42": "Zodiark", "56": "Phoenix", "66": "Odin", "67": "Shiva",
    "402": "Alpha", "403": "Raiden", "39": "Omega", "71": "Moogle", "80": "Cerberus", "83": "Louisoix",
    "85": "Spriggan", "97": "Ragnarok", "400": "Sagittarius", "401": "Phantom"
}

STATUS_DICT = {
    "1": "Preparation: Talk to NPC to start",
    "2": "Running",
    "3": "Completed",
    "4": "FATE FAILED"
}

FATE_TO_HUNT_MAP = {
    1259: 5986,  # Orghana
    831: 4375,  # Senmurv
    556: 2961,  # Minhocao
    1862: 13399,  # Sansheya
    1871: 1,
    1922: 1
}

HUNT_TO_COOLDOWN_MAP = {
    5986: 84 * 3600,  # Orghana
    4375: 84 * 3600,  # Senmurv
    2961: 57 * 3600,  # Minhocao
    13399: 84 * 3600,  # Sansheya
    1: 2 * 2
}

EU_IDS = [33, 36, 42, 56, 66, 67, 402, 403, 39, 71, 80, 83, 85, 97, 400, 401]

CATEGORY_A = [2936, 2937, 2938, 2939, 2940, 2941, 2942, 2943, 2944, 2945, 2946, 2947, 2948, 2949, 2950, 2951, 2952, 4362, 4363, 4364, 4365, 4366, 4367, 4368, 4369, 4370, 4371, 4372, 4373, 5996, 5997, 5998, 5999, 6000, 6001, 5990, 5991, 5992, 5993, 5994, 5995, 8906, 8907, 8911, 8912, 8901, 8902, 8654, 8655, 8891, 8892, 8896, 8897, 10624, 10623, 10625, 10626, 10627, 10628, 10630, 10629, 10632, 10631, 10634, 10633, 13361, 13362, 13442, 13443, 12692, 12753, 13400, 13401, 13157, 13158, 13435, 13436]
CATEGORY_B = [2919, 2920, 2921, 2922, 2923, 2924, 2925, 2926, 2927, 2928, 2929, 2930, 2931, 2932, 2933, 2934, 2935, 4350, 4351, 4352, 4353, 4354, 4355, 4356, 4357, 4358, 4359, 4360, 4361, 6002, 6003, 6004, 6005, 6006, 6007, 6008, 6009, 6010, 6011, 6012, 6013, 8908, 8909, 8913, 8914, 8903, 8904, 8656, 8657, 8893, 8894, 8898, 8899, 10635, 10636, 10637, 10638, 10639, 10640, 10641, 10642, 10643, 10644, 10645, 10646, 13144, 13145, 13146, 13147, 13148, 13149, 13150, 13151, 13152, 13153, 13154, 13155]
CATEGORY_S = [2953, 2954, 2955, 2956, 2957, 2958, 2959, 2960, 2961, 2962, 2963, 2964, 2965, 2966, 2967, 2968, 2969, 4374, 4375, 4376, 4377, 4378, 4380, 5984, 5985, 5986, 5987, 5988, 5989, 8905, 8910, 8900, 8653, 8890, 8895, 8915, 10617, 10615, 10618, 10619, 10620, 10621, 10622, 13360, 13444, 12754, 13399, 13156, 13437]
CATEGORY_SS = [8915, 10615, 13406, 8916, 10616, 13407]

HUNT_CATEGORY_MAP = {
    "A": CATEGORY_A,
    "B": CATEGORY_B,
    "S": CATEGORY_S,
}
