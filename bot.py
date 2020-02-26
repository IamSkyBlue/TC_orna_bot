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
    bot.add_cog(RR(bot))
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


class RR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lastRefreshTime = 99999
        self.data = []
        self.dataRefresh.start()


    @tasks.loop(minutes=10)
    async def dataRefresh(self):
        url = 'http://indextracker.ga/'
        try:
            html = requests.get(url).content.decode('utf-8')
        except requests.exceptions.Timeout:
            return
        sp = BeautifulSoup(html,'html.parser')
        newRefreshTime = int(sp.select('footer div div')[0].text.split(' ')[18])
        if sp.select('footer div div')[0].text.split(' ')[19][0] == 'h':
            newRefreshTime *= 60
        if sp.select('footer div div')[0].text.split(' ')[19][0] == 's':
            newRefreshTime = 0
        if self.lastRefreshTime > newRefreshTime:
            print('data has been changed, catching data...')
            self.data = [item.text for item in sp.find_all('td')]
            self.lastRefreshTime = newRefreshTime
            print('done')

    @dataRefresh.before_loop
    async def before_dataRefresh(self):
        print('waiting to start loop...')
        await self.bot.wait_until_ready()

    @commands.command(name='rr', help='使用方法: ~rr <health|mil|edu|dev>')
    async def health(self, ctx, col):
        indexNameList = ['健康','軍事','教育','發展']
        if col == "health":
            dataIndex = 0
        elif col == "mil":
            dataIndex = 1
        elif col == "edu":
            dataIndex = 2
        elif col == "dev":
            dataIndex = 3
        else:
            await ctx.send('錯誤的項目名稱，請使用health, mil, edu, dev')
            return
        title = indexNameList[dataIndex] + "指數的建築物數量︰"
        msg = "Last update " + str(self.lastRefreshTime) +" hours ago"
        embed=discord.Embed(title=title)
        embed.add_field(name="10 - ", value=self.data[dataIndex*10 + 0], inline=True)
        embed.add_field(name="9 - ", value=self.data[dataIndex*10 + 1], inline=False)
        embed.add_field(name="8 - ", value=self.data[dataIndex*10 + 2], inline=False)
        embed.add_field(name="7 - ", value=self.data[dataIndex*10 + 3], inline=False)
        embed.add_field(name="6 - ", value=self.data[dataIndex*10 + 4], inline=False)
        embed.add_field(name="5 - ", value=self.data[dataIndex*10 + 5], inline=False)
        embed.add_field(name="4 - ", value=self.data[dataIndex*10 + 6], inline=False)
        embed.add_field(name="3 - ", value=self.data[dataIndex*10 + 7], inline=False)
        embed.add_field(name="2 - ", value=self.data[dataIndex*10 + 8], inline=False)
        embed.add_field(name="1 - ", value="0", inline=False)
        embed.set_footer(text=msg)
        await ctx.send(embed=embed)


bot.run(token)