import babel
from babel.numbers import format_decimal
from resources.langs import en, it

lang_obj = {
	"en": en,
	"it": it
}


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