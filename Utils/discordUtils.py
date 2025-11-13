import json
import httpx
import discord
import asyncio
import sqlite3
from datetime import datetime, timezone, timedelta

#------URL Constants---------#
BASE_URL = "https://www.habbo.com"
USER_URL = "api/public/users"

def getConfig():
    """Reads and returns the configuration dictionary from config.json."""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("Error: config.json not found.")
        return {}
    except json.JSONDecodeError:
        print("Error: Invalid JSON in config.json.")
        return {}


def getWatchlist():
    """Reads and returns the watchlist dictionary from watchlist.json."""
    try:
        with open('watchlist.json', 'r') as f:
            wlist = json.load(f)
        return wlist
    except FileNotFoundError:
        print("Error: watchlist.json not found.")
        return {}
    except json.JSONDecodeError:
        print("Error: Invalid JSON in watchlist.json.")
        return {}

def setWatchlist(wlist : dict):
    """Writes the given watchlist dictionary to watchlist.json."""
    with open('watchlist.json', 'w') as f:
        json.dump(wlist, f)

async def gethabbo(username : str):
    """Fetches Habbo user data, including status and lastAccessTime."""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url= f'{BASE_URL}/{USER_URL}', params= {'name' : username})
            data = r.json()
        print(data)
        
        final = {'status' : bool(data['online']),
                 'name' : data['name'],
                 'lastAccessTime': data.get('lastAccessTime') 
                 }
        
        return final
    except Exception:
        print(f'Error retrieving habbo profile from api. profile id {username} --- ')
        return None

async def get_thread_by_name(channel: discord.TextChannel, thread_name: str) -> discord.Thread | None:
    """Finds an active thread in a channel by its name."""
    for thread in channel.threads:
        if thread.name == thread_name:
            return thread
    return None

def parse_time_string(time_str: str) -> datetime | None:
    """
    Parses time strings from Habbo API or stored ISO 8601 format into a UTC datetime object.
    """
    if not time_str:
        return None
    try:
        if '+' in time_str:
             # Habbo API format: 2025-11-05T20:34:00.000+0000
             return datetime.strptime(time_str[:-5], '%Y-%m-%dT%H:%M:%S.%f').replace(tzinfo=timezone.utc)
        elif time_str.endswith('Z'):
             # Database ISO format: 2025-11-06T16:52:24.123456Z
             return datetime.strptime(time_str.split('.')[0], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
        else:
             return None
    except ValueError:
        return None

def format_duration(start_time_str: str) -> str | None:
    """
    Calculates the time difference between the stored login time (start) and the current UTC time (end).
    """
    online_since_dt = parse_time_string(start_time_str)
    
    # --- Use the current date/time as the end time (logout detection time) ---
    offline_time_dt = datetime.now(timezone.utc) 
    
    # Check for valid times and ensure logout time is after login time
    if not online_since_dt or offline_time_dt <= online_since_dt:
        return None
    
    time_online: timedelta = offline_time_dt - online_since_dt

    seconds = int(time_online.total_seconds())
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    duration_parts = []
    if days > 0:
        duration_parts.append(f'{days} day{"s" if days != 1 else ""}')
    if hours > 0:
        duration_parts.append(f'{hours} hour{"s" if hours != 1 else ""}')
    if minutes > 0:
        duration_parts.append(f'{minutes} minute{"s" if minutes != 1 else ""}')

    return ', '.join(duration_parts) if duration_parts else 'a moment'


async def send_online_update(bot, channelid : int, username : str, habbo_data: dict ):
    """Sends the status update and calculates online duration using current time as logout."""
    
    chan = await bot.fetch_channel(channelid)
    status = habbo_data.get('status')
    
    if chan is None or not isinstance(chan, discord.Thread):
        print(f'channel is not a thread or not found: ID {channelid}')
        return

    description = f'🟢 {username} is now **ONLINE!**' if status == True else f'🔴 {username} is now **OFFLINE!** '
    c = discord.Color.green() if status == True else discord.Color.red()
        
    # --- DURATION LOGIC ---
    if status == False:
        # Retrieve the necessary login time passed from apicaller.py
        online_since = habbo_data.get('lastAccessTime') 
        
        # Calculate duration using stored login time and CURRENT time
        duration_str = format_duration(online_since) 
        
        if duration_str:
            description += f'They were online for **{duration_str}**.'
        else:
            description += f'*Online duration could not be accurately calculated.*'
    # --- END DURATION LOGIC ---

    embed = discord.Embed(title=f'User {username}', description= description, color = c)
    embed.set_footer(icon_url= bot.user.avatar.url, text= f'{bot.user.name} . {datetime.utcnow()}')

    await chan.send(embed=embed)


async def send_view_profile_update(bot, channelid : int, username : str, status : bool ):
    """Sends a profile status update."""
    chan = bot.get_channel(channelid)
    thread = await get_thread_by_name(chan, username)

    if thread is None:
        print(f"Error: Could not find thread for {username} in channel {channelid}")
        return

    v = 'Public' if status == True else 'Private'

    embed = discord.Embed(title='User Changed profile status', description= f"{username}'s profile is now {v}" , color = discord.Color.blue())
    embed.set_footer(icon_url= bot.user.avatar.url, text= f'{bot.user} . {datetime.utcnow()}')

    await thread.send(embed=embed)