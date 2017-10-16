"""
this file is for the leaderboard ordering groups by amount of members sent in an interval
"""
from src import dbwrapper as db
from src import constants as c
from src.objects_leaderboard import Leaderboard
from src import utils
from config import config

from telegram import Bot

def members(far_interval, lang, limit, receiver):
	name_type = 'members'
	query_near = """
		SELECT 
			m.group_id,
			m.amount, 
			s_ref.title, 
			s_ref.username, 
			s.nsfw
		FROM
		-- Window function to get only de last_date:
		    (
			SELECT 
				last_members.group_id,
				last_members.amount
			FROM
			    (
			    SELECT 
				    *,
				    ROW_NUMBER() 
				  	OVER (
				    PARTITION BY group_id
				    ORDER BY updated_date DESC) AS row 
				FROM members
			) AS last_members
			WHERE last_members.row=1
			) AS m
		-- Joins with other tables
		LEFT JOIN supergroups AS s
		ON m.group_id = s.group_id
		LEFT JOIN supergroups_ref AS s_ref
		ON s.group_id = s_ref.group_id
		WHERE 
			(s.banned_until IS NULL OR s.banned_until < now()) 
			AND lang = %s
		ORDER BY m.amount DESC, m.group_id DESC
		LIMIT %s
		"""
	near_stats = db.query_r(query_near, lang, limit)
	

	query_far = """
		SELECT 
			m.group_id,
			m.amount, 
			s_ref.title, 
			s_ref.username, 
			s.nsfw
		FROM
		-- Window function to get only de last_date:
		    (
			SELECT 
				last_members.group_id,
				last_members.amount
			FROM
			    (
			    SELECT 
				    *,
				    ROW_NUMBER() 
				  	OVER (
				    PARTITION BY group_id
				    ORDER BY updated_date DESC) AS row 
				FROM members
				WHERE updated_date <= now() - interval %s
			) AS last_members
			WHERE last_members.row=1
			) AS m
		-- Joins with other tables
		LEFT JOIN supergroups AS s
		ON m.group_id = s.group_id
		LEFT JOIN supergroups_ref AS s_ref
		ON s.group_id = s_ref.group_id
		WHERE 
			(s.banned_until IS NULL OR s.banned_until < now()) 
			AND lang = %s
		ORDER BY m.amount DESC, m.group_id DESC
		LIMIT %s
		"""

	far_stats = db.query_r(query_far, far_interval, lang, limit)

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
		except AttributeError:
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
		message += "{}) {}@{}: {}{}\n".format(
						i.position, i.nsfw, i.username, utils.sep_l(num=amount, locale=lang), position
			)

	utils.save_already_joined(name_type=name_type, lang=lang, to_save=already_joined)
	
	message += "\n\nout:"
	got_out = []
	for i in out:
		nsfw = "" if i.nsfw is False else c.NSFW_E
		element = "{}@{}".format(nsfw, i.username)
		got_out.append(element)
	message += ' '.join(got_out)

	Bot(config.BOT_TOKEN).sendMessage(chat_id=receiver, text=message, parse_mode='HTML')