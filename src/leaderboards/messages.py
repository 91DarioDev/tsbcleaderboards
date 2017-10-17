"""
this file is for the leaderboard ordering groups by amount of messages sent in an interval
"""
from src import dbwrapper as db
from src import constants as c
from src.objects_leaderboard import Leaderboard
from src import utils
from resources.langs import en, it
from config import config

from telegram import Bot

def messages(near_interval, far_interval, lang, limit, receiver):
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
		t_id.set_diff_value()
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

	message = utils.get_string(lang, "intro_messages")
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
			position
			)

	utils.save_already_joined(name_type=name_type, lang=lang, to_save=already_joined)
	
	got_out = []
	for i in out:
		nsfw = "" if i.nsfw is False else c.NSFW_E
		element = "{}@{}".format(nsfw, i.username)
		got_out.append(element)

	if len(got_out) > 0:
		message += "\n\n{}<b>{}</b>".format(c.BASKET_E, utils.get_string(lang, "out"))
		message += ', '.join(got_out)

	Bot(config.BOT_TOKEN).sendMessage(
			chat_id=receiver, 
			text=message, 
			parse_mode='HTML',
			disable_notification=True)
	
	Bot(config.BOT_TOKEN).sendDocument(
			chat_id=config.ADMIN_ID, 
			document=open(utils.get_name(name_type, lang), 'rb'),
			disable_notification=True)