import babel
from babel.numbers import format_decimal

def get_name(name_type, lang):
	return "already_joined/{}_{}.txt".format(name_type, lang)

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
	try:
		file = open(get_name(name_type, lang), 'w')
		file.write('\n'.join(to_save))
	except Exception as e:
		print(e)
	finally:
		file.close()


def sep(num, none_is_zero=False):
	if num is None:
		return 0 if none_is_zero is False else None
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