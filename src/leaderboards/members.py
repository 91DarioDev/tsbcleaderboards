"""
this file is for the leaderboard ordering groups by amount of members sent in an interval
"""


# TSBCleaderboards - An extension of TopSupergroupsBot to post leaderboards 
# on a channel on intervals
#
# Copyright (C) 2017  Dario <dariomsn@hotmail.it> (github.com/91DarioDev)
#
# TSBCleaderboards is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TSBCleaderboards is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TSBCleaderboards.  If not, see <http://www.gnu.org/licenses/>.



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
            members.*,  
            supergroups_ref.title, 
            supergroups_ref.username, 
            extract(epoch from supergroups.joined_the_bot at time zone 'utc') AS dt,
            supergroups.nsfw,
            RANK() OVER (PARTITION BY supergroups.lang ORDER BY members.amount DESC)
        FROM
        -- Window function to get only de last_date:
            (SELECT last_members.group_id,last_members.amount
            FROM
            (SELECT *, ROW_NUMBER() OVER (PARTITION BY group_id
            ORDER BY updated_date DESC) AS row FROM members) AS last_members
            WHERE last_members.row=1) AS members
        -- Joins with other tables
        LEFT JOIN supergroups
        ON members.group_id = supergroups.group_id
        LEFT JOIN supergroups_ref 
        ON supergroups.group_id = supergroups_ref.group_id
        WHERE (supergroups.banned_until IS NULL OR supergroups.banned_until < now()) 
        	AND lang = %s
        LIMIT %s
		"""
	near_stats = db.query_r(query_near, lang, limit)
	

	query_far = """
        SELECT 
            members.*,  
            supergroups_ref.title, 
            supergroups_ref.username, 
            extract(epoch from supergroups.joined_the_bot at time zone 'utc') AS dt,
            supergroups.nsfw,
            RANK() OVER (PARTITION BY supergroups.lang ORDER BY members.amount DESC)
        FROM
        -- Window function to get only de last_date:
            (SELECT last_members.group_id,last_members.amount
            FROM
            (SELECT *, ROW_NUMBER() OVER (PARTITION BY group_id
            ORDER BY updated_date DESC) AS row FROM members
            WHERE updated_date <= now() - interval %s
            ) AS last_members
            WHERE last_members.row=1) AS members
        -- Joins with other tables
        LEFT JOIN supergroups
        ON members.group_id = supergroups.group_id
        LEFT JOIN supergroups_ref 
        ON supergroups.group_id = supergroups_ref.group_id
        WHERE (supergroups.banned_until IS NULL OR supergroups.banned_until < now()) 
        	AND lang = %s
        LIMIT %s
		"""

	#####################
	#  EXTRACTING DATA
	#####################


	far_stats = db.query_r(query_far, far_interval, lang, limit)

	far_list = []
	for i in far_stats:
		far_list.append([i[0], i[1], i[2], i[3], i[4], i[6]])


	leaderboard_list = []
	for i in near_stats:
		t_id = i[0]
		t_id = Leaderboard(
			tg_id=i[0],
			value=i[1], 
			position=i[6], 
			title=i[2], 
			username=i[3], 
			nsfw=i[5])
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
				last_position=i[5],
				title=i[2],
				username=i[3],
				nsfw=i[4])
			out.append(t_id)


	# GET LIST OF ALREADY JOINED
	already_joined = utils.get_already_joined(name_type=name_type, lang=lang)

	#####################
	# CREATING THE TEXT
	#####################

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


	# SAVE NEW ALREADY JOINED LIST
	utils.save_already_joined(name_type=name_type, lang=lang, to_save=already_joined)
	

	###############
	#   GOT OUT
	###############

	got_out = []
	for i in out:
		nsfw = "" if i.nsfw is False else c.NSFW_E
		element = "{}@{}".format(nsfw, i.username)
		got_out.append(element)

	if len(got_out) > 0:
		message += "\n\n{}<b>{}</b>".format(c.BASKET_E, utils.get_string(lang, "out"))
		message += ', '.join(got_out)


	lst = [i for i in leaderboard_list if i.diff_value is not None]

	#################
	# MOST INCREASED
	#################

	
	try:
		max_value = max([e.diff_value for e in lst])
		most_increased = [i for i in leaderboard_list if i.diff_value == max_value]
	except ValueError:  # the list is empty
		most_increased = []


	if len(most_increased) > 0:
		strings = []
		for i in most_increased:
			string = "{}@{}({})".format(
					"" if i.nsfw is False else c.NSFW_E,
					i.username,
					utils.sep_l(i.diff_value, lang))
			strings.append(string)
		message += '\n\n{}<b>{}</b>'.format(
				c.MOST_INCREASED_E, 
				utils.get_string(lang, 'most_increased'))
		message += ', '.join(strings)

	

	##########################
	# MOST INCREASED PERCENT
	##########################

	try:
		max_value = max([e.diff_percent for e in lst])
		most_incr_percent = [i for i in leaderboard_list if i.diff_percent == max_value]
	except ValueError:
		most_incr_percent = []

	if len(most_incr_percent) > 0:
		strings = []
		for i in most_incr_percent:
			string = "{}@{}({}%)".format(
					"" if i.nsfw is False else c.NSFW_E,
					i.username,
					round(i.diff_percent, 2))
			strings.append(string)
		message += '\n\n{}<b>{}</b>'.format(
				c.MOST_INCR_PERCENT_E, 
				utils.get_string(lang, 'most_incr_percent'))
		message += ', '.join(strings)





	#################
	# SEND MESSAGE
	#################

	Bot(config.BOT_TOKEN).sendMessage(
			chat_id=receiver, 
			text=message, 
			parse_mode='HTML',
			disable_notification=True)
	

	###############
	# SEND BACKUP
	###############

	Bot(config.BOT_TOKEN).sendDocument(
			chat_id=config.ADMIN_ID, 
			document=open(utils.get_name(name_type, lang), 'rb'),
			disable_notification=True)