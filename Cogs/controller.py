import discord
from discord.ext import commands
from Utils.discordUtils import  gethabbo
import httpx
import datetime
import asyncio
#------URL Constants---------#
BASE_URL = "https://www.habbo.com"
USER_URL = "api/public/users"


class ControllerCog(commands.Cog):

	def __init__(self,bot):
		self.bot = bot

	




	watchlistgroup = discord.SlashCommandGroup("watchlist", "Commands to add/remove/edit users in the watchlist")

	@watchlistgroup.command()
	async def add(self, ctx:discord.ApplicationContext, username : str):

		await ctx.response.defer()
		

		user = await gethabbo(username)

		if user is None:
			await ctx.followup.send(f'Unable to find user with the username {username}. Please verify if username is correct')
		else:
			dbUser = self.bot.database.get_user(username)
			if dbUser is None:
				
				await ctx.followup.send(f"{username} added to this channel's watchlist.")
				user['channels'] = [ctx.channel_id]
				self.bot.database.insert_user(user)
				
			else:
				await ctx.followup.send(f"{username} added to this channel's watchlist.")
				dbUser['channels'].append(ctx.channel_id)
				self.bot.database.insert_user(dbUser, name=username)
			
   


	@watchlistgroup.command()
	async def remove(self, ctx:discord.ApplicationContext, username : str):

		await ctx.response.defer()

		user = self.bot.database.get_user(username)
  
		if user is not None:
			try:
				user['channels'].remove(ctx.channel_id)
				if len(user['channels']) == 0:
					self.bot.database.cleanup_user(username)
				else:
					self.bot.database.insert_user(user, name=username)
				await ctx.followup.send(f"{username} removed from this channel's watchlist", ephemeral=True)
			except KeyError:
				await ctx.followup.send(f"{username} is not on this channel's watchlist", ephemeral=True)

  	

	@watchlistgroup.command()
	async def list(self, ctx:discord.ApplicationContext):

		await ctx.response.defer()
  
		try:
			db = self.bot.database.db.items()
			usernamelist = [item[0]for item in db if ctx.channel_id in item[1]['channels']]
			usernamelist.sort(key=str.lower)

			embed = discord.Embed(title="Watchlist for this channel", description = '\n'.join(usernamelist), color = discord.Color.random())
			embed.set_footer(icon_url= self.bot.user.avatar, text= f'{self.bot.user.name} . {datetime.datetime.utcnow()}')
			await ctx.followup.send(embed=embed)
		except KeyError:
			await ctx.followup.send("Watchlist is empty.")
  
	@watchlistgroup.command()
	async def cleanup(self, ctx:discord.ApplicationContext):

		await ctx.response.defer()

		channellist = [channel.id for channel in self.bot.get_all_channels()]
		db = self.bot.database.db
		counter = 0
		for item in db.items():
			for channelid in item[1]['channels']:
				if channelid not in channelid:
					self.bot.database.clean_channel(channelid)
					counter += 1
		await ctx.followup.send(f"{counter} number of invalid channel references cleaned", ephemeral=True)



#-----setup------#

def setup(bot):
	bot.add_cog(ControllerCog(bot))




