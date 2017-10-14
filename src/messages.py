"""
this file is for the leaderboard ordering groups by amount of messages sent in an interval
"""
from src import dbwrapper as db

def messages(near_interval, far_interval, lang, limit, bot_token):
	query_near = """
		SELECT
			group_id,
			COUNT(msg_id) AS leaderboard,
			s_ref.title,
			s_ref.username,
			s.nsfw
		FROM messages AS m
		LEFT OUTER JOIN supergroups AS s
		USING (group_id)
		LEFT OUTER JOIN supergroups_ref AS s_ref
		USING (group_id)
		WHERE
			m.message_date > (now() - interval %s)
			AND (s.banned_until IS NULL OR s.banned_until < now()) 
			AND s.lang = %s
		GROUP BY group_id, s_ref.title, s_ref.username, s.nsfw
		ORDER BY leaderboard, group_id DESC
		LIMIT %s
		"""

	near_stats  = db.query_r(query_near, near_interval, lang, limit)

	query_far = """
		SELECT
			group_id,
			COUNT(msg_id) AS leaderboard,
			s_ref.title,
			s_ref.username,
			s.nsfw
		FROM messages AS m
		LEFT OUTER JOIN supergroups AS s
		USING (group_id)
		LEFT OUTER JOIN supergroups_ref AS s_ref
		USING (group_id)
		WHERE
			m.message_date BETWEEN (now() - interval %s) AND (now() - interval %s)
			AND (s.banned_until IS NULL OR s.banned_until < now()) 
			AND s.lang = %s
		GROUP BY group_id, s_ref.title, s_ref.username, s.nsfw
		ORDER BY leaderboard, group_id DESC
		LIMIT %s
		"""

	far_stats = db.query_r(query_far, far_interval, near_interval, lang, limit)

	print(far_stats)