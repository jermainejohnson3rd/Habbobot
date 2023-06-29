import json
import httpx
import discord
import asyncio
import datetime
import sqlite3

#------URL Constants---------#
BASE_URL = "https://www.habbo.com"
USER_URL = "api/public/users"

def getConfig():

	with open('config.json', 'r') as f:
		config = json.load(f)

	return config


def getWatchlist():

	with open('watchlist.json', 'r') as f:
		wlist = json.load(f)

	return wlist

def setWatchlist(wlist : dict):

	with open('watchlist.json', 'w') as f:
		json.dump(wlist, f)

async def gethabbo(username : str):
		
		try:
			async with httpx.AsyncClient() as client:
				r = await client.get(url= f'{BASE_URL}/{USER_URL}', params= {'name' : username})
				data = r.json()
			print(data)
			
			final = {'status' : bool(data['online']),
					 'name' : data['name'],
					 }
			
			return final
		except:
			print(f'Error retrieving habbo profile from api. profile id {username} --- ')
			return None


async def send_online_update(bot, channelid : int, username : str, status : bool ):

		chan = bot.get_channel(channelid)
		a = 'Online' if status == True else 'Offline'
		c = discord.Color.green() if status == True else discord.Color.red()
		embed = discord.Embed(title=f'User {a}', description= f'{username} is now {a}', color = c)
		embed.set_footer(icon_url= bot.user.avatar,text= f'{bot.user.name} . {datetime.datetime.utcnow()}')

		await chan.send(embed=embed)



async def send_view_profile_update(bot, channelid : int, username : str, status : bool ):

	chan = bot.get_channel(channelid)

	v = 'Public' if status == True else 'Private'

	embed = discord.Embed(title='User Changed profile status', description= f"{username}'s profile is now {v}" , color = discord.Color.blue())
	embed.set_footer(icon_url= bot.user.avatar, text= f'{bot.user} . {datetime.datetime.utcnow()}')

	await chan.send(embed=embed)

#db- int manager


