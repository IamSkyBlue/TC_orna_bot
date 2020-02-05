# encoding: utf-8
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

import pygsheets

load_dotenv()
gc = pygsheets.authorize(service_account_env_var = 'GDRIVE_API_CREDENTIALS')
sh = gc.open('Ornabook')
wks = sh[0]

token = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='~')

@bot.event
async def on_ready():
    print('connected to Discord!')

@bot.command(name='search')
async def search(ctx,name,category='orna'):
    titles=wks.find(name,cols=(1,1),matchEntireCell=True)
    if not titles:
        try:
            await ctx.send('尚無資料，歡迎至 https://tinyurl.com/wxa9qxy 新增資料')
        except:
             pass
        return
    for title in titles:
        for item in wks.get_row(title.row,include_tailing_empty=False)[1::]:
            try:
                await ctx.send(item)
            except:
                pass

bot.run(token)