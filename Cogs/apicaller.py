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
		

		wlist = getWatchlist()

		for userid in wlist:
			h = await gethabbo(userid)
			if h is not None:
				if h['status'] != bool(wlist[userid]['status']):
					wlist[userid]['status'] = h['status']
					for channelid in wlist[userid]['channels']:
						await send_online_update(self.bot,int(channelid), h['name'], bool(h['status']))

		setWatchlist(wlist)












		# for channelid in wlist:
		# 	for userdict in wlist[channelid]:
		# 		id = userdict['id']

				
		# 		h = await gethabbo(id)
		# 		if h is not None:
		# 			if h['status'] != bool(userdict['status']):
		# 				#func to send online status embed message

		# 				userdict['status'] = h['status']

		# 				await send_online_update(self.bot,int(channelid), h['name'], bool(h['status']))
		# 			#this part is unnecessary. turns out private profiles arte not indexed so this whole thing is pointless
		# 			elif h['viewprofile'] != bool(userdict['viewprofile']):
						
		# 				userdict['viewprofile'] = h['viewprofile']

		# 				await send_view_profile_update(self.bot,int(channelid), h['name'], bool(h['viewprofile']))

		# setWatchlist(wlist)





#-----setup------#

def setup(bot):
	bot.add_cog(Apicaller(bot))



# {'userid' : {'name' : 'ashjdgajsd', 'channels' : [1232131,123123123], 'status' : true}}



