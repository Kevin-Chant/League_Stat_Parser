import os
import json
import datetime
import riot_api_access as riot
from stats import *

def store_json(json_obj, filename, force=False):
    if os.path.isfile(filename) and not force:
        print("Cannot store at " + filename + ".\nFile already exists.")
        return False
    if not isinstance(json_obj, dict):
        print("Must be given a valid dictionary to store")
        return False
    with open(filename, 'w') as fp:
        json.dump(json_obj, fp)
        return True

def load_json(filename):
    if not os.path.isfile(filename):
        print("File cannot be found")
        return None
    with open(filename) as fp:
        return json.load(fp)

def download_match_with_cache(match_id):
    match = load_json(".match_cache/" + str(match_id) + ".json")
    if not match:
        match = riot.get_match_from_id(match_id)
    store_json(match, ".match_cache/" + str(match_id) + ".json", True)
    return match

def update_champ_ids(force=False):
    dct = riot.get_champion_id_dict()
    if not store_json(dct, "champ_ids.json", force):
        return None
    return dct

def convert_champ_id_to_name(id):
    dct = load_json("champ_ids.json")
    if not dct:
        dct = update_champ_ids()
    return dct[str(id)]

def convert_champ_name_to_id(name):
    dct = load_json("champ_ids.json")
    if not dct:
        dct = update_champ_ids()
    for id in dct:
        if dct[id] == name:
            return int(id)

def update_match_manifest(match_ids, player_dict_lists):
    manifest = load_json(".match_cache/.manifest.json")
    if not manifest:
        manifest = {}
    for i in range(len(match_ids)):
        manifest[match_ids[i]] = player_dict_lists[i]
    store_json(manifest, ".match_cache/.manifest.json", True)
    return manifest

def date_to_epoch(month, day, year):
    dt = datetime.datetime(year, month, day)
    return int((dt-datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000)

def get_and_cache_user_history(summonername, start_epoch=None, end_epoch=None, champion=None, lane_role=None):
    aid = riot.get_account_id(summonername)
    history = riot.get_match_history(aid, start_epoch, end_epoch, champion)["matches"]
    stats = stats_from_filtered_matches([match["gameId"] for match in history], summonername, [], [], lane_role)
    return stats


# stats = get_and_cache_user_history("Alanegod93", date_to_epoch(3, 24, 2018), date_to_epoch(3, 29, 2018), None, ("BOTTOM", "DUO_CARRY"))
# print(stats)