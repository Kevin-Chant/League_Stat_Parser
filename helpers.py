import os
import json
from riot_api_access import *

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
    match = load_json(str(match_id) + ".json")
    if not match:
        match = get_match_from_id(match_id)
    store_json(match, ".match_cache/" + str(match_id) + ".json", True)
    return match

def update_champ_ids(force=False):
    dct = get_champion_id_dict()
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