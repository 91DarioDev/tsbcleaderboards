"""
this is an example of how to launch a leaderboard
"""
import src
import config

src.messages.messages(near_interval='7 days', 
					far_interval='14 days', 
					lang='it', 
					limit=50, 
					bot_token=config.config.BOT_TOKEN)
