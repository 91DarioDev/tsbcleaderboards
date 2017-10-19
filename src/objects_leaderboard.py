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




class Leaderboard:
	def __init__(self, 
				tg_id,
				value=None, 
				position=None, 
				last_value=None, 
				last_position=None,
				nsfw=False,
				title=None,
				username=None):

		self.tg_id = tg_id
		self.value = value
		self.position = position
		self.last_value = last_value
		self.last_position = last_position
		self.nsfw = nsfw
		self.title = title
		self.username = username

	def set_diff_value(self):
		if self.value is None or self.last_value is None:
			self.diff_value = None
			self.diff_percent = None
		else:
			self.diff_value = self.value - self.last_value
			self.diff_percent = (self.value-self.last_value)*100/last_value