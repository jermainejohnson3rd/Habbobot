import discord
from discord.ext import commands, tasks
import json
import httpx
from Utils.discordUtils import getConfig, getWatchlist, setWatchlist, gethabbo, send_online_update, send_view_profile_update
import datetime as dt
import asyncio


class Apicaller(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.get_user_status.start()

	def cog_unload(self):
		self.get_user_status.cancel()

	
	


	




#------ main loop----------#
	#main tasks
	@tasks.loop(seconds= 60)	
	async def get_user_status(self):


		for item in self.bot.database.db.items():
			h = await gethabbo(item[0])
			if h is not None:
				if h['status'] != bool(item[1]['status']):
					item[1]['status'] = h['status']
					for channelid in item[1]['channels']:
						try:
							await send_online_update(self.bot,int(channelid), h['name'], bool(h['status']))
						except:
							print('error sending message on channel: ' + channelid)
					self.bot.database.insert_user(item[1], item[0])
	
 
	@commands.Cog.listener()
	async def on_guild_channel_delete(self, channel):
		self.bot.database.clean_channel(channel.id)



#-----setup------#

def setup(bot):
	bot.add_cog(Apicaller(bot))






