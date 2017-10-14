"""
This file contains wrapped queries for the db
"""

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