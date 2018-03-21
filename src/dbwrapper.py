"""
This file contains wrapped queries for the db
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



import threading
import psycopg2
from config import config

#                            _   _          
#    __ ___ _ _  _ _  ___ __| |_(_)___ _ _  
#   / _/ _ \ ' \| ' \/ -_) _|  _| / _ \ ' \ 
#   \__\___/_||_|_||_\___\__|\__|_\___/_||_|
#        


def conn():
	local = threading.local()

	if not hasattr(local, "db"):
		local.db = psycopg2.connect(config.POSTGRES_DB)
	return local.db


#                                      _                     _        
#   __ __ ___ _ __ _ _ __ _ __  ___ __| |  __ _ _  _ ___ _ _(_)___ ___
#   \ V  V / '_/ _` | '_ \ '_ \/ -_) _` | / _` | || / -_) '_| / -_|_-<
#    \_/\_/|_| \__,_| .__/ .__/\___\__,_| \__, |\_,_\___|_| |_\___/__/
#                   |_|  |_|                 |_|                      



def query_w(query, *params):
	connect = conn()
	c = connect.cursor()
	c.execute(query, params)
	c.connection.commit()
	c.close()

def query_r(query, *params, one=False):
	connect = conn()
	c = connect.cursor()
	c.execute(query, params)
	try:
		if not one:
			return c.fetchall()
		else:
			return c.fetchone()
	finally:
		c.close()


def query_wr(query, *params, one=False):
	connect = conn()
	c = connect.cursor()
	c.execute(query, params)
	c.connection.commit()
	try:
		if not one:
			return c.fetchall()
		else:
			return c.fetchone()
	finally:
		c.close()