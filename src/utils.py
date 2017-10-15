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