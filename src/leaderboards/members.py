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
        	AND supergroups.bot_inside IS TRUE
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
        	AND supergroups.bot_inside IS TRUE
        LIMIT %s
		"""

	#####################
	#  EXTRACTING DATA
	#####################
############################################à

	far_stats = db.query_r(query_far, far_interval, lang, limit)

	near_stats_ids = [i[0] for i in near_stats]
	far_stats_ids = [i[0] for i in far_stats]

	# GET LIST OF ALREADY JOINED
	already_joined = utils.get_already_joined(name_type=name_type, lang=lang)

	diff_value_dct = {}
	usernames_dct = {}
	nsfw_dct = {}
	diff_value_percent_dct = {}
	message = utils.get_string(lang, "intro_members") 
	for i in near_stats:
		pos = i[6]
		nsfw = "" if i[5] is False else c.NSFW_E
		nsfw_dct[i[0]] = nsfw
		username = i[3]
		usernames_dct[i[0]] = username
		value = i[1]

		if str(i[0]) not in already_joined:
			value = utils.sep_l(value, lang)
			diff_pos = c.NEW_E
			already_joined.append(str(i[0]))
		else:
			if i[0] in far_stats_ids:
				for e in far_stats:
					if e[0] == i[0]:
						diff_value = value - e[1]
						diff_pos = e[6] - pos #pos - e[6]
						diff_value_dct[i[0]] = diff_value
						diff_value_percent_dct[i[0]] = (value-e[1])*100/e[1]

						value = "<b>"+utils.sep_l(value, lang)+"</b>" if (diff_value >= 0) else "<i>"+utils.sep_l(value, lang)+"</i>"
						if diff_pos > 0:
							diff_pos = c.UP_POS_E+"+"+str(diff_pos)
						elif diff_pos < 0:
							diff_pos = c.DOWN_POS_E+str(diff_pos)
						else:
							diff_pos = ""

						break
			else:
				value = utils.sep_l(value, lang)
				diff_pos = c.BACK_E

		message += "{}) {}@{} {} {}{}\n".format(pos, nsfw, username, c.MEMBERS_E, value, diff_pos)

	# SAVE NEW ALREADY JOINED LIST
	utils.save_already_joined(name_type=name_type, lang=lang, to_save=already_joined)

	###############
	#   GOT OUT
	###############

	got_out = []
	for i in far_stats:
		if i[0] not in near_stats_ids:
			nsfw = "" if i[5] is False else c.NSFW_E
			element = "{}@{}".format(nsfw, i[3])
			got_out.append(element)

	if len(got_out) > 0:
		message += "\n\n{}<b>{}</b>".format(c.BASKET_E, utils.get_string(lang, "out"))
		message += ', '.join(got_out)

	##################
	# MOST INCREASED #
	##################

	try:
		max_value = max(diff_value_dct.values())
		most_increased = [i for i in diff_value_dct if diff_value_dct[i] == max_value]
	except ValueError:  # the list is empty
		most_increased = []


	if len(most_increased) > 0:
		strings = []
		for i in most_increased:
			string = "{}@{}({})".format(
					nsfw_dct[i],
					usernames_dct[i],
					utils.sep_l(max_value, lang))
			strings.append(string)
		message += '\n\n{}<b>{}</b>'.format(
				c.MOST_INCREASED_E, 
				utils.get_string(lang, 'most_increased'))
		message += ', '.join(strings)	

	
	##########################
	# MOST INCREASED PERCENT #
	##########################

	try:
		max_value = max(diff_value_percent_dct.values())
		most_incr_percent = [i for i in diff_value_percent_dct if diff_value_percent_dct[i] == max_value]
	except ValueError:
		most_incr_percent = []

	if len(most_incr_percent) > 0:
		strings = []
		for i in most_incr_percent:
			string = "{}@{}({}%)".format(
					nsfw_dct[i],
					usernames_dct[i],
					round(max_value, 2))
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
			disable_notification=True,
			reply_markup=utils.about_you_kb(lang)
			)
	

	###############
	# SEND BACKUP
	###############

	Bot(config.BOT_TOKEN).sendDocument(
			chat_id=config.ADMIN_ID, 
			document=open(utils.get_name(name_type, lang), 'rb'),
			disable_notification=True)

