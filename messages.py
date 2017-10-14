"""
this file is for the leaderboard ordering groups by amount of messages sent in an interval
"""

NEAR_INTERVAL = '7 days'
FAR_INTERVAL = '14 days'


def messages():
	query = """
		SELECT
			group_id
			COUNT (msg_id) AS leaderboard,
			s_ref.title,
			s_ref.username,
			s.nsfw
		FROM messages
		LEFT OUTER JOIN supergroups AS s
		USING (group_id)
		LEFT OUTER JOIN supergrousp_ref AS s_ref
		USING (group_id)
		WHERE
			message_date > (now() - interval %s)
			AND (s.banned_until IS NULL OR s.banned_until < now()) 
			AND s.lang = %s
		GROUP BY group_id, s_ref.title, s_ref.username, s.nsfw
		ORDER BY leaderboard, group_id DESC
		LIMIT %s
		"""