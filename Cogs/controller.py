import discord
from discord.ext import commands
from Utils.discordUtils import getWatchlist, setWatchlist
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
		
		try:
			async with httpx.AsyncClient() as client:
				r =  await client.get(url = f'{BASE_URL}/{USER_URL}', params = {'name' : username})
				user = r.json()
				print(user)
				id = user['uniqueId']
		except:
			print(f'Error getting user from username {username}')
			id =  None

		if id is None:
			await ctx.followup.send(f'Unable to find user with the username {username}. Please verify if username is correct')
		else:
			await ctx.followup.send(f"{username} added to this channel's watchlist.")
			wlist = getWatchlist()

			if id in wlist.keys():
				wlist[id]['channels'].append(ctx.channel_id)
			else:
				wlist[id] = {'name' : username,
							 'channels' : [ctx.channel_id],
							 'status' : False}

			setWatchlist(wlist)


	@watchlistgroup.command()
	async def remove(self, ctx:discord.ApplicationContext, username : str):

		await ctx.response.defer()
		await asyncio.sleep(1)

		wlist = getWatchlist()
		try:
			for key, value in wlist.items():

				if value['name'] == username :
					try:
						value['channels'].remove(ctx.channel_id)
						if len(value['channels']) == 0:
							wlist.pop(key)

						await ctx.followup.send(f"{username} removed from this channel's watchlist")
						setWatchlist(wlist)
						break
					except:
						await ctx.followup.send(f"{username} is not on this channel's watchlist")
						break
		except:
			await ctx.followup.send(f"{username} is not on this channel's watchlist")


			

	@watchlistgroup.command()
	async def list(self, ctx:discord.ApplicationContext):

		await ctx.response.defer()
		await asyncio.sleep(1)
		wlist = getWatchlist()
		try:
			username_list = [wlist[item]['name'] for item in wlist if ctx.channel_id in wlist[item]['channels']]

			embed = discord.Embed(title="Watchlist for this channel", description = '\n'.join(username_list), color = discord.Color.random())
			embed.set_footer(icon_url= self.bot.user.avatar, text= f'{self.bot.user.name} . {datetime.datetime.utcnow()}')
			await ctx.followup.send(embed=embed)
		except KeyError:
			await ctx.followup.send("Watchlist is empty.")

		


#-----setup------#

def setup(bot):
	bot.add_cog(ControllerCog(bot))




