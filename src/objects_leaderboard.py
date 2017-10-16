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
		self.diff_value = (value-last_value) if value is not None and last_value is not None else None