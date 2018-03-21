"""
this is an example of how to launch a leaderboard
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



from src.leaderboards import messages, members, votes
import config

messages.messages(near_interval='7 days', 
		far_interval='14 days', 
		lang='it', 
		limit=50,
		receiver=1234567890)

members.members(far_interval='7 days', 
		lang='it', 
		limit=50,
		receiver=1234567890)

votes.votes(interval='7 days', 
		lang='it', 
		limit=50,
		min_reviews=10,
		receiver=1234567890)