"""
This file contains constants
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

from config import config
from telegram import Bot


UP_POS_E = "🔼"
DOWN_POS_E = "🔽"
BACK_E = "🔙"
NEW_E = "🆕"
NSFW_E = "🔞"
BASKET_E = "🗑"
MOST_INCREASED_E = "🔝"
MOST_INCR_PERCENT_E = "📈"
MEMBERS_E = "👥"
MESSAGES_E = "💬"

GET_ME = Bot(config.BOT_TOKEN).getMe()