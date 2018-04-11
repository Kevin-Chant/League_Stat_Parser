from global_defs import *
def get_all_champ_stats(match_obj):
	stats = {}
	for ban in match_obj["teams"][0]["bans"] + match_obj["teams"][1]["bans"]:
		stats[ban["championId"]] = BANNED_CHAMP_STATS.copy()
	for participant in match_obj["participants"]:
		champ_stats = {}
		champ_id = participant["championId"]
		for stat in TRACKED_CHAMPION_STATS:
			champ_stats[stat] = STAT_COLLECTION_METHODS[stat](match_obj, champ_id)

		stats[champ_id] = champ_stats
	return stats

def agg_champ_stats(match_objs):
	stats = {}
	for m_ob in match_objs:
		match_stats = get_all_champ_stats(m_ob)
		for cid in match_stats:
			if cid not in stats:
				stats[cid] = match_stats[cid]
			else:
				for key in match_stats[cid]:
					stats[cid][key] += match_stats[cid][key]
	return stats

def calculate_ods(stats):
	ods = {}
	for stat in STAT_CALCULATION_METHODS:
		ods[stat] = STAT_CALCULATION_METHODS[stat](stats)
	return ods