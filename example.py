"""
this is an example of how to launch a leaderboard
"""
from src.leaderboards import messages
import config

messages.messages(near_interval='7 days', 
					far_interval='14 days', 
					lang='it', 
					limit=50,
					receiver=1234567)