# encoding: utf-8
import os
import re

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

import pygsheets
from bs4 import BeautifulSoup
import requests

load_dotenv()
gc = pygsheets.authorize(service_account_env_var = 'GDRIVE_API_CREDENTIALS')
sh = gc.open('Ornabook')
wks = sh[0]

token = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='~',description='Orna字典機器人, 透過社群的力量建起的機器人\n一起貢獻: https://tinyurl.com/wxa9qxy\nlittle RR index bot RR地區指數查詢機器人')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="~help 取得幫助"))
    bot.add_cog(Orna(bot))
    print('connected to Discord!')

class Orna(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='status', help='使用方法: ~status 可查詢遊戲伺服器狀態')
    async def status(self, ctx):
        ornaStatusList = ["遊戲本體","地圖","官網"]
        url = 'https://orna.statuspal.io/'
        html = requests.get(url).content.decode('utf-8')
        sp = BeautifulSoup(html,'html.parser')
        for serviceNmae,link in zip(ornaStatusList,sp.find_all("span", class_="service-status--status")):
            await ctx.send("{0:{2}<4}: {1:}".format(serviceNmae,link.text[1::],chr(12288)))

    @commands.command(name='search', help='使用方法: ~search <要搜尋的東西> |搜尋規則或幫助: ~search help')
    async def search(self, ctx,name):
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

    @commands.command(name='poll', help='使用方法: ~poll "投票名稱" "項目一" "項目二"..... 中間記得空格')
    async def poll(self, ctx, *args):
        emojiLetters = [
            "\N{REGIONAL INDICATOR SYMBOL LETTER A}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER B}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER C}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER D}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER E}", 
            "\N{REGIONAL INDICATOR SYMBOL LETTER F}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER G}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER H}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER I}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER J}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER K}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER L}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER M}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER N}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER O}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER P}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER Q}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER R}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER S}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER T}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER U}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER V}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER W}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER X}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER Y}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER Z}"
        ]
        if len(args)>27:
            await ctx.send('創建失敗，請勿超過26個選項')
            return
        if len(args)==1:
            await ctx.send('創建失敗，至少要有1個選項')
            return
        await ctx.send('\N{Bar Chart} **' + args[0] + '**')
        optionMessage = ""
        for i,item in enumerate(args[1::]):
            optionMessage = optionMessage + emojiLetters[i] + ' ' + item + "\n"
        embed=discord.Embed(description=optionMessage,color=0x0000e1)
        pollMessage = await ctx.send(embed=embed)
        for i,item in enumerate(args[1::]):
            await pollMessage.add_reaction(emojiLetters[i])

bot.run(token)