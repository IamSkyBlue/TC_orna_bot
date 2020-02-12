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

@bot.command(name='search', help='\'~search <something>\' | \'~search help\' to see help')
async def search(ctx,name,category='orna'):
    if name == 'index':
        message = '資料庫已有目錄: ```'
        indexString = ' , '.join(sorted(wks.get_col(1,include_tailing_empty=False)[1::]))
        message =message + indexString + '```'
        await ctx.send(message)
        return
    matchTitleRow = [ title.row for title in wks.get_col(1, returnas='cell', include_tailing_empty=False)[1::] if title.value == name]
    if not matchTitleRow:
        try:
            await ctx.send('尚無資料，歡迎至 https://tinyurl.com/wxa9qxy 新增資料')
        except:
             pass
        return
    for row in matchTitleRow:
        message = '\n---\n'.join(wks.get_row(row,include_tailing_empty=False)[1::])
        try:
            await ctx.send(message)
        except:
            pass

bot.run(token)