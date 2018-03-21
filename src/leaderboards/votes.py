"""
this file is for the leaderboard ordering groups by amount of votes
"""


# TSBCleaderboards - An extension of TopSupergroupsBot to post leaderboards 
# on a channel on intervals
#
# Copyright (C) 2017-2018  Dario <dariomsn@hotmail.it> (github.com/91DarioDev)
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
from resources.langs import en, it
from config import config

from telegram import Bot


def votes(interval, lang, limit, receiver, min_reviews):
	name_type = 'votes'
	query_near = """
        SELECT
            group_id,
            COUNT(vote) AS amount,
            ROUND(AVG(vote), 1) AS average, 
            RANK() OVER(PARTITION BY s.lang ORDER BY ROUND(AVG(VOTE), 1)DESC, COUNT(VOTE)DESC),
            s.nsfw,
            s_ref.username
        FROM votes 
        LEFT OUTER JOIN supergroups AS s 
        USING (group_id)
        GROUP BY group_id, s.lang, s.banned_until, s.bot_inside
        HAVING 
            (s.banned_until IS NULL OR s.banned_until < now()) 
            AND s.lang = %s
            AND COUNT(vote) >= %s 
            AND s.bot_inside IS TRUE
        LIMIT %s
    """


	#####################
	#  EXTRACTING DATA
	#####################

	near_stats  = db.query_r(query_near, lang, min_reviews, limit)

	query_far = """
        SELECT 
            group_id,
            COUNT(vote) AS amount,
            ROUND(AVG(vote), 1) AS average, 
            RANK() OVER(PARTITION BY s.lang ORDER BY ROUND(AVG(VOTE), 1)DESC, COUNT(VOTE)DESC),
            s.nsfw,
            s_ref.username
        FROM votes
        LEFT OUTER JOIN supergroups AS s 
        USING (group_id)
        WHERE vote_date <= now() - interval %s
        GROUP BY group_id, s.lang, s.banned_until, s.bot_inside
        HAVING 
            (s.banned_until IS NULL OR s.banned_until < now())
            AND s.lang = %s
            AND COUNT(vote) >= %s 
            AND s.bot_inside IS TRUE
        LIMIT %s
    """

	
	far_stats = db.query_r(query_far, interval, lang, min_reviews, limit)
	
	near_stats_ids = [i[0] for i in near_stats]
	far_stats_ids = [i[0] for i in far_stats]

	# GET LIST OF ALREADY JOINED
	already_joined = utils.get_already_joined(name_type=name_type, lang=lang)

	

	message = utils.get_string(lang, "intro_votes") 
	for i in near_stats:
		pos = i[3]
		nsfw = "" if i[4] is False else c.NSFW_E
		username = i[5]
		value = i[2]
		amount_of_votes = i[1]

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

		message += "{}) {}@{} {} {}{}({}){}\n".format(pos, nsfw, username, c.MESSAGES_E, value, c.STAR_E, utils.sep_l(amount_of_votes, lang), diff_pos)


	# SAVE NEW ALREADY JOINED LIST
	utils.save_already_joined(name_type=name_type, lang=lang, to_save=already_joined)

	###############
	#   GOT OUT
	###############

	got_out = []
	for i in far_stats:
		if i[0] not in near_stats_ids:
			nsfw = "" if i[4] is False else c.NSFW_E
			element = "{}@{}".format(nsfw, i[5])
			got_out.append(element)

	if len(got_out) > 0:
		message += "\n\n{}<b>{}</b>".format(c.BASKET_E, utils.get_string(lang, "out"))
		message += ', '.join(got_out)

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

