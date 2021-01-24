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
        WITH myconst AS
        (SELECT 
	    s.lang,
	    AVG(vote)::float AS overall_avg
	FROM votes AS v
	LEFT OUTER JOIN supergroups AS s
	ON s.group_id = v.group_id
	WHERE (s.banned_until IS NULL OR s.banned_until < now() )
	AND s.bot_inside IS TRUE
	GROUP BY s.lang
	HAVING COUNT(vote) >= %s)

        SELECT 
          *,
          RANK() OVER (PARTITION BY sub.lang  ORDER BY bayesan DESC)
          FROM (
            SELECT 
                v.group_id,
                s_ref.title, 
                s_ref.username, 
                COUNT(vote) AS amount, 
                ROUND(AVG(vote), 1)::float AS average,
                s.nsfw,
                extract(epoch from s.joined_the_bot at time zone 'utc') AS dt,
                s.lang,
                s.category,
                -- (WR) = (v ÷ (v+m)) × R + (m ÷ (v+m)) × C
                --    * R = average for the movie (mean) = (Rating)
                --    * v = number of votes for the movie = (votes)
                --    * m = minimum votes required to be listed in the Top 250 (currently 1300)
                --    * C = the mean vote across the whole report (currently 6.8)
                (  (COUNT(vote)::float / (COUNT(vote)+%s)) * AVG(vote)::float + (%s::float / (COUNT(vote)+%s)) * (m.overall_avg) ) AS bayesan
            FROM votes AS v
            LEFT OUTER JOIN supergroups_ref AS s_ref
            ON s_ref.group_id = v.group_id
            LEFT OUTER JOIN supergroups AS s
            ON s.group_id = v.group_id
            LEFT OUTER JOIN myconst AS m
            ON (s.lang = m.lang)
            GROUP BY v.group_id, s_ref.title, s_ref.username, s.nsfw, s.banned_until, s.lang, s.category, s.bot_inside, s.joined_the_bot, m.overall_avg
            HAVING 
                (s.banned_until IS NULL OR s.banned_until < now()) 
                AND COUNT(vote) >= %s
                AND s.lang = %s
                AND s.bot_inside IS TRUE
          ) AS sub
          LIMIT %s;
    """


	#####################
	#  EXTRACTING DATA
	#####################

	near_stats  = db.query_r(
		query_near, 
		min_reviews,
		min_reviews,
		min_reviews,
		min_reviews,
		min_reviews,
		lang,
		limit
	)

	query_far = """
        WITH myconst AS
        (SELECT 
	    s.lang,
	    AVG(vote)::float AS overall_avg
	FROM votes AS v
	LEFT OUTER JOIN supergroups AS s
	ON s.group_id = v.group_id
	WHERE (s.banned_until IS NULL OR s.banned_until < now() ) AND WHERE vote_date <= now() - interval %s
	AND s.bot_inside IS TRUE
	GROUP BY s.lang
	HAVING COUNT(vote) >= %s)

        SELECT 
          *,
          RANK() OVER (PARTITION BY sub.lang  ORDER BY bayesan DESC)
          FROM (
            SELECT 
                v.group_id,
                s_ref.title, 
                s_ref.username, 
                COUNT(vote) AS amount, 
                ROUND(AVG(vote), 1)::float AS average,
                s.nsfw,
                extract(epoch from s.joined_the_bot at time zone 'utc') AS dt,
                s.lang,
                s.category,
                -- (WR) = (v ÷ (v+m)) × R + (m ÷ (v+m)) × C
                --    * R = average for the movie (mean) = (Rating)
                --    * v = number of votes for the movie = (votes)
                --    * m = minimum votes required to be listed in the Top 250 (currently 1300)
                --    * C = the mean vote across the whole report (currently 6.8)
                (  (COUNT(vote)::float / (COUNT(vote)+%s)) * AVG(vote)::float + (%s::float / (COUNT(vote)+%s)) * (m.overall_avg) ) AS bayesan
            FROM votes AS v
            LEFT OUTER JOIN supergroups_ref AS s_ref
            ON s_ref.group_id = v.group_id
            LEFT OUTER JOIN supergroups AS s
            ON s.group_id = v.group_id
            LEFT OUTER JOIN myconst AS m
            ON (s.lang = m.lang)
            WHERE vote_date <= now() - interval %s
            GROUP BY v.group_id, s_ref.title, s_ref.username, s.nsfw, s.banned_until, s.lang, s.category, s.bot_inside, s.joined_the_bot, m.overall_avg
            HAVING 
                (s.banned_until IS NULL OR s.banned_until < now()) 
                AND COUNT(vote) >= %s
                AND s.lang = %s
                AND s.bot_inside IS TRUE
          ) AS sub
          LIMIT %s;
    """

	far_stats = db.query_r(
		query_far, 
		interval,
		min_reviews,
		min_reviews,
		min_reviews,
		min_reviews,
		interval,
		min_reviews,
		lang,
		limit
	)
	
	near_stats_ids = [i[0] for i in near_stats]
	far_stats_ids = [i[0] for i in far_stats]

	# GET LIST OF ALREADY JOINED
	already_joined = utils.get_already_joined(name_type=name_type, lang=lang)

	
	diff_value_dct = {}
	usernames_dct = {}
	nsfw_dct = {}
	diff_value_percent_dct = {}
	message = utils.get_string(lang, "intro_votes") 
	for i in near_stats:
		pos = i[10]
		nsfw = "" if i[5] is False else c.NSFW_E
		username = i[2]
		value = i[4]
		amount_of_votes = i[3]
		usernames_dct[i[0]] = username
		nsfw_dct[i[0]] = nsfw


		if str(i[0]) not in already_joined:
			value = utils.sep_l(value, lang)
			diff_pos = c.NEW_E
			already_joined.append(str(i[0]))
		else:
			if i[0] in far_stats_ids:
				for e in far_stats:
					if e[0] == i[0]:
						diff_value = value - e[4]
						diff_pos = e[10] - pos #pos - e[3]
						diff_value_dct[i[0]] = diff_value
						diff_value_percent_dct[i[0]] = (value-e[4])*100/e[4]

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

		message += "{}) {}@{}  {}{}({}){}\n".format(pos, nsfw, username, value, c.STAR_E, utils.sep_l(amount_of_votes, lang), diff_pos)


	# SAVE NEW ALREADY JOINED LIST
	utils.save_already_joined(name_type=name_type, lang=lang, to_save=already_joined)

	###############
	#   GOT OUT
	###############

	got_out = []
	for i in far_stats:
		if i[0] not in near_stats_ids:
			nsfw = "" if i[5] is False else c.NSFW_E
			element = "{}@{}".format(nsfw, i[2])
			got_out.append(element)

	if len(got_out) > 0:
		message += "\n\n{}<b>{}</b>".format(c.BASKET_E, utils.get_string(lang, "out"))
		message += ', '.join(got_out)






	##################
	# MOST INCREASED #
	##################

	try:
		max_value = max(diff_value_dct.values())
		most_increased = [i for i in diff_value_dct if (diff_value_dct[i] == max_value and max_value > 0)]
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
		most_incr_percent = [i for i in diff_value_percent_dct if (diff_value_percent_dct[i] == max_value and max_value > 0)]
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

