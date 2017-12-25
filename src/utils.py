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



import babel
from babel.numbers import format_decimal
from resources.langs import en, it
from config import config

lang_obj = {
	"en": en,
	"it": it
}


def get_name(name_type, lang):
	return config.PATH+"already_joined/{}_{}.txt".format(name_type, lang)



def get_already_joined(name_type, lang):
	file_name = get_name(name_type, lang)
	try:
		file = open(file_name, 'r')
		already_joined = file.read().splitlines()
	except FileNotFoundError:
		# create the file
		file = open(file_name, 'w')
		already_joined = []
	finally:
		file.close()
	return already_joined


def save_already_joined(name_type, lang, to_save):
	file_name = get_name(name_type, lang)
	try:
		file = open(file_name, 'w')
		file.write('\n'.join(to_save))
	except Exception as e:
		print(e)
	finally:
		file.close()


def sep(num, none_is_zero=False):
	if num is None:
		return 0 if none_is_zero is True else None
	return "{:,}".format(num)




def sep_l(num, locale='en', none_is_zero=False):
	if num is None:
		return None if none_is_zero is False else 0
	if locale is None:
		return "{:,}".format(num)
	try:
		return babel.numbers.format_decimal(num, locale=locale)
	except babel.core.UnknownLocaleError:
		return "{:,}".format(num)





def get_string(lang, variable):
	"""
	returns the right string. example of usage:
	print(get_string("en", "test"))
	'en' is the language of the user returned from the db
	'"test"' is the name of the variable in the relative file lang
	"""

	try:
		string = getattr(lang_obj[lang], variable)
	except AttributeError:
		string = getattr(en, variable)
	except KeyError:
		string = getattr(en, variable)
	return string