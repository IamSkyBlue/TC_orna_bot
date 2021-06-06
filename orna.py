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
Ornabook = gc.open("Ornabook")
mainwks = Ornabook[0]
wordwks = Ornabook[1]

OrnaTCDB = gc.open("OrnaTCDB")
TCDBmainwks = OrnaTCDB[0]


class Orna(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="search",
        help="使用方法: ~search <要搜尋的東西> |搜尋規則或幫助: ~search help| ~search index 可察看目錄",
    )
    async def search(self, ctx, name):
        if name == "index":
            result = mainwks.get_col(1, include_tailing_empty=False)[1::]
            await ctx.send("資料庫已有目錄: ")
            while result:
                indexString = "```index"
                while len(indexString) < 1900 and result:
                    indexItem = result.pop(0)
                    if indexItem:
                        indexString = indexString + "," + indexItem
                await ctx.send(indexString + "```")
            return

        matchTitleRow = [
            title.row
            for title in mainwks.get_col(
                1, returnas="cell", include_tailing_empty=False
            )[1::]
            if title.value == name
        ]
        if not matchTitleRow:
            try:
                await ctx.send(
                    "主要資料庫無資料，已將詞彙加入待新增詞彙庫，歡迎至 <https://tinyurl.com/wxa9qxy> 新增資料"
                )
                await ctx.send(
                    "或是可以到中文圖書館自己尋找有用的資訊 <https://hackmd.io/@Iamskyblue/Orna_TW_index>"
                )
                matchTitleRow_wordwks = [
                    title.row
                    for title in wordwks.get_col(
                        1, returnas="cell", include_tailing_empty=False
                    )[1::]
                    if title.value == name
                ]
                if not matchTitleRow_wordwks:
                    wordwks.insert_rows(1, values=[name, "", "", "", "", ""])
            except Exception as e:
                print(e)
            return
        for row in matchTitleRow:
            message = "\n---\n".join(
                mainwks.get_row(row, include_tailing_empty=False)[1::]
            )
            try:
                await ctx.send(message)
            except Exception as e:
                print(e)

    @commands.command(
        name="translate",
        help="使用方法: ~translate <要翻譯的東西> | 中英皆可，但必須要一字不差才能搜尋到",
    )
    async def translate(self, ctx, *searchctx):
        name = " ".join(str(i) for i in searchctx)
        name = name.lower()
        if name.isascii():  # english to chinese
            searchcol = 2
            resultcol = 3
        else:  # chinese to english
            searchcol = 3
            resultcol = 2

        matchTitleRow = [
            title.row
            for title in TCDBmainwks.get_col(
                searchcol, returnas="cell", include_tailing_empty=False
            )[2::]
            if title.value.lower() == name
        ]
        if not matchTitleRow:
            updatetime = OrnaTCDB.updated[:10]
            await ctx.send("資料庫中無符合資料，請注意是否有錯字，也可能是本資料庫未更新最新字串")
            await ctx.send("本資料庫最後更新時間為: " + updatetime)
        for row in matchTitleRow[1::]:  # some string has duplicate translate
            message = TCDBmainwks.cell((row, resultcol)).value
            await ctx.send(message)


def setup(bot):
    bot.add_cog(Orna(bot))