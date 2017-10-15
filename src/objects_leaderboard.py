class Leaderboard:
	def __init__(self, 
				value=None, 
				position=None, 
				last_value=None, 
				last_position=None,
				nsfw=False,
				title=None,
				username=None
				):

		self.value = value
		self.position = position
		self.last_value = last_value
		self.last_position = last_position
		self.nsfw = nsfw
		self.title = title
		self.username = username