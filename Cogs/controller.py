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
            return # Added return to stop execution

        # --- Logic to determine the thread and get the ID to store ---
        thread_id_to_store = None
        
        if isinstance(ctx.channel, discord.Thread): # Correct class name
            # If command is run inside a thread, use that thread's ID.
            thread_id_to_store = ctx.channel_id 
        else:
            # If command is run in a text channel, create a new thread.
            thread = await ctx.channel.create_thread(
                name=username
            )
            thread_id_to_store = thread.id
        
        # --- End of thread determination logic ---
        
        dbUser = self.bot.database.get_user(username)
        
        if dbUser is None:
            # New user being watched
            user['channels'] = [thread_id_to_store]
            self.bot.database.insert_user(user)
            await ctx.followup.send(f"{username} added to this channel's watchlist.")
            
        else:
            # Existing user being watched
            if thread_id_to_store in dbUser['channels']:
                await ctx.followup.send(f"{username} is already on this channel's watchlist.", ephemeral=True)
                return
            
            # Append the new thread ID to the existing list of channels/threads
            dbUser['channels'].append(thread_id_to_store) # Correctly using dbUser
            self.bot.database.insert_user(dbUser, name=username)
            await ctx.followup.send(f"{username} added to this channel's watchlist.")


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




