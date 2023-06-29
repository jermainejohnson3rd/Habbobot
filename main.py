import httpx
import discord
from discord.ext import commands
from Utils.dbUtils import DbUtil
import os, json



intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='?', intents = intents)

bot.remove_command('help')

bot.database = DbUtil("data.sqlite", tablename="Watchlist")

if __name__ == '__main__':
	for filename in os.listdir('Cogs'):
		if filename.endswith('.py'):
			bot.load_extension(f'Cogs.{filename[:-3]}')


@bot.event
async def on_ready():
	print(f'Logged in as botuser {bot.user}')
	print(f'discord version {discord.__version__}')
	



#-------------------RUN------------------------#
with open('config.json', 'r') as config:
	data = json.load(config)
	token = data['token']

bot.run(token)


