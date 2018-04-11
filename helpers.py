import os
import json
import datetime
import time
import riot_api_access as riot

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

def find_id_in_list(id, fieldname, lst):
    for dct in lst:
        if str(dct[fieldname]).lower() == str(id).lower():
            return dct

def find_matching_fields_in_list(value, fieldname, lst):
    matches = []
    for dct in lst:
        if str(dct[fieldname]).lower() == str(value).lower():
            matches.append(dct)
    return matches

def get_subfields_in_list(fieldname, lst):
    fields = []
    for dct in lst:
        if fieldname in dct:
            fields.append(dct[fieldname])
    return fields

def get_name_from_partic_id(match_obj, partic_id):
    partic_obj = find_id_in_list(partic_id, "participantId", match_obj["participantIdentities"])
    if "player" in partic_obj:
        return partic_obj["player"]["summonerName"]

def clean(name):
    return "".join(name.split(" ")).lower()

def get_partic_id_from_name(match_obj, summoner_name):
    for partic_identity in match_obj["participantIdentities"]:
        if "player" in partic_identity and "summonerName" in partic_identity["player"] and clean(partic_identity["player"]["summonerName"]) == clean(summoner_name):
            return partic_identity["participantId"]
    return None

def get_opponent(participants, participant_id):
    participant_role = find_id_in_list(participant_id, "participantId", participants)["timeline"]["role"]
    for other in participants:
        if participant_id != other["participantId"] and other["timeline"]["role"] == participant_role:
            return other

def convert_cs_diff(cs_diff_by_min, gamelength):
    for duration in cs_diff_by_min:
        if "end" not in duration:
            cs_diff_by_min[duration] = round(cs_diff_by_min[duration] * 10, 2)
        else:
            cs_diff_by_min[duration] = round(cs_diff_by_min[duration] * float(gamelength-int(duration[:2])*60)/60, 2)
    return cs_diff_by_min

def date_to_epoch(month=None, day=None, year=None):
    if not month and not day and not year:
        return int(time.time())*1000
    dt = datetime.datetime(year, month, day)
    return int((dt-datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000)+28800000