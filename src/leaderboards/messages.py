"""
this file is for the leaderboard ordering groups by amount of messages sent in an interval
"""
from src import dbwrapper as db
from src import constants as c
from src.objects_leaderboard import Leaderboard
import src.utils as utils

def messages(near_interval, far_interval, lang, limit, bot_token):
	name_type = 'messages'
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
		ORDER BY leaderboard DESC, group_id DESC
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
		ORDER BY leaderboard DESC, group_id DESC
		LIMIT %s
		"""

	far_stats = db.query_r(query_far, far_interval, near_interval, lang, limit)

	leaderboard_list = []
	count = 0
	for i in near_stats:
		count += 1
		t_id = i[0]
		t_id = Leaderboard(tg_id=i[0],
							value=i[1], 
							position=count, 
							title=i[2], 
							username=i[3], 
							nsfw=i[4])
		leaderboard_list.append(t_id)


	out = []
	count = 0
	for i in far_stats:
		count += 1
		t_id = i[0]
		try:
			t_id.last_value = i[1]
			t_id.last_position = count
		except NameError:
			t_id = Leaderboard(tg_id=i[0],
								last_value=i[1],
								last_position=count,
								title=i[2],
								username=i[3],
								nsfw=i[4])
			out.append(t_id)


	already_joined = utils.get_already_joined(name_type=name_type, lang=lang)

	message = ""
	for i in leaderboard_list:
		i.nsfw = "" if i.nsfw is False else c.NSFW_E
		if i.last_value is None:
			amount = i.value
			position = ""
			if str(i.tg_id) in already_joined:
				position = c.BACK_E
			else:
				position = c.NEW_E
				already_joined.append(str(i.tg_id))
		else:
			amount = "<b>"+str(i.value)+"</b>" if (i.value - i.last_value >= 0) else "<i>"+str(i.value)+"</i>"
			diff_pos = i.position - i.last_position
			if diff_pos > 0:
				position = c.UP_POS_E+"+"+str(diff_pos)
			elif diff_pos < 0:
				position = c.DOWN_POS_E+str(diff_pos)
			else:
				position = ""
		message += "{}) {}@{}: {}{}".format(
						i.position, i.nsfw, i.username, amount, position
			)

	utils.save_already_joined(name_type=name_type, lang=lang, to_save=already_joined)
	
	message += "\n\nout:"
	got_out = []
	for i in out:
		nsfw = "" if i.nsfw is False else c.NSFW_E
		element = "{}@{}".format(nsfw, i.username)
		got_out.append(element)
	message += ' '.join(got_out)