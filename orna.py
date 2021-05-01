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
gc = pygsheets.authorize(service_account_env_var="GDRIVE_API_CREDENTIALS")
sh = gc.open("Ornabook")
wks = sh[0]


class Orna(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="search", help="使用方法: ~search <要搜尋的東西> |搜尋規則或幫助: ~search help"
    )
    async def search(self, ctx, name):
        if name == "index":
            message = "資料庫已有目錄: ```"
            indexString = " , ".join(
                sorted(wks.get_col(1, include_tailing_empty=False)[1::])
            )
            message = message + indexString + "```"
            await ctx.send(message)
            return
        matchTitleRow = [
            title.row
            for title in wks.get_col(1, returnas="cell", include_tailing_empty=False)[
                1::
            ]
            if title.value == name
        ]
        if not matchTitleRow:
            try:
                await ctx.send("尚無資料，歡迎至 <https://tinyurl.com/wxa9qxy> 新增資料")
                await ctx.send(
                    "或是可以到中文圖書館自己尋找有用的資訊 <https://hackmd.io/@Iamskyblue/Orna_TW_index>"
                )
            except:
                pass
            return
        for row in matchTitleRow:
            message = "\n---\n".join(wks.get_row(row, include_tailing_empty=False)[1::])
            try:
                await ctx.send(message)
            except:
                pass
