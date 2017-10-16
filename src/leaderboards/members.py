"""
this file is for the leaderboard ordering groups by amount of members sent in an interval
"""
from src import dbwrapper as db
from src import constants as c
from src.objects_leaderboard import Leaderboard
from src import utils
from config import config

from operator import attrgetter

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

	far_list = []
	count = 0
	for i in far_stats:
		count += 1
		far_list.append([i[0], i[1], i[2], i[3], i[4], count])


	leaderboard_list = []
	count = 0
	for i in near_stats:
		count += 1
		t_id = i[0]
		t_id = Leaderboard(
			tg_id=i[0],
			value=i[1], 
			position=count, 
			title=i[2], 
			username=i[3], 
			nsfw=i[4])
		for sub_i in far_list:
			if sub_i[0] == i[0]:
				t_id.last_value = sub_i[1]
				t_id.last_position = sub_i[5]
				break
		leaderboard_list.append(t_id)


	out = []
	id_current = [i.tg_id for i in leaderboard_list]
	for i in far_list:
		if i[0] not in id_current:
			t_id = Leaderboard(
				tg_id=i[0],
				last_value=i[1],
				last_position=count,
				title=i[2],
				username=i[3],
				nsfw=i[4])
			out.append(t_id)


	already_joined = utils.get_already_joined(name_type=name_type, lang=lang)

	message = utils.get_string(lang, "intro_members")
	for i in leaderboard_list:
		i.nsfw = "" if i.nsfw is False else c.NSFW_E
		
		if str(i.tg_id) not in already_joined:
			amount = utils.sep_l(i.value, lang)
			position = c.NEW_E
			already_joined.append(str(i.tg_id))
		
		elif i.last_value is None:
			amount = utils.sep_l(i.value, lang)
			position = c.BACK_E

		else:
			amount = "<b>"+utils.sep_l(i.value, lang)+"</b>" if (i.diff_value >= 0) else "<i>"+utils.sep_l(i.value, lang)+"</i>"
			diff_pos = i.position - i.last_position
			if diff_pos > 0:
				position = c.UP_POS_E+"+"+str(diff_pos)
			elif diff_pos < 0:
				position = c.DOWN_POS_E+str(diff_pos)
			else:
				position = ""

		message += "{}) {}@{}: {}{}\n".format(
			i.position, 
			i.nsfw, 
			i.username, 
			amount, 
			position)

	utils.save_already_joined(name_type=name_type, lang=lang, to_save=already_joined)
	
	message += "\n\n{}{}".format(c.BASKET_E, utils.get_string(lang, "out"))
	got_out = []
	for i in out:
		nsfw = "" if i.nsfw is False else c.NSFW_E
		element = "{}@{}".format(nsfw, i.username)
		got_out.append(element)
	message += ', '.join(got_out)

	lst = [i.position for i in leaderboard_list if i.diff_value is not None]
	try:
		most_increased = max(lst, key=attrgetter('diff_value'))
	except ValueError:  # the list is empty
		most_increased = None


	if most_increased is not None:
		message += '\n{}{}: {}{}'.format(
			c.MOST_INCREASED_E,
			get_string(lang, 'most_increased'),
			"" if most_increased.nsfw is False else c.NSFW_E,
			most_increased.username)


	Bot(config.BOT_TOKEN).sendMessage(
			chat_id=receiver, 
			text=message, 
			parse_mode='HTML',
			disable_notification=True)
	
	Bot(config.BOT_TOKEN).sendDocument(
			chat_id=config.ADMIN_ID, 
			document=open(utils.get_name(name_type, lang), 'rb'),
			disable_notification=True)