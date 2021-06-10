# encoding: utf-8
import os
import time

import discord
from discord.ext import commands, tasks

from dotenv import load_dotenv

import pygsheets

from google.cloud import vision

load_dotenv()
gc = pygsheets.authorize(service_account_env_var="GOOGLE_CREDENTIALS")
Ornabook = gc.open("Ornabook")
mainwks = Ornabook[0]
wordwks = Ornabook[1]

OrnaTCDB = gc.open("OrnaTCDB")
TCDBmainwks = OrnaTCDB[0]
imgporcesschannels = OrnaTCDB[1]

visionclient = vision.ImageAnnotatorClient()

IMAGE_TYPE = ("jpeg", "png", "webp")
MATCH_WORD_TC = (
    "血量:",
    "魔力:",
    "護盾:",
    "物攻:",
    "物防:",
    "敏捷:",
    "魔攻:",
    "魔防:",
    "爆擊:",
    "+視線範圍",
    "-視線範圍",
    "+經驗加成",
    "-經驗加成",
    "+金幣加成",
    "-金幣加成",
    "+歐幣加成",
    "-歐幣加成",
)
MATCH_WORD_EN = (
    "HP:",
    "Mana:",
    "Ward:",
    "Att:",
    "Def:",
    "Dex:",
    "Mag:",
    "Res:",
    "Crit:",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
)


class Orna(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.updatetime = time.time()
        self.imgporcesschannellist = imgporcesschannels.get_all_values(
            returnas="matrix",
            majdim="ROWS",
            include_tailing_empty=False,
            include_tailing_empty_rows=False,
        )[1::]

    @commands.command(
        name="search",
        help="使用方法: ~search <要搜尋的東西> |搜尋規則或幫助: ~search help| ~search index 可察看目錄",
    )
    async def search(self, ctx, *searchctx):
        name = " ".join(str(i) for i in searchctx)
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
            return

        message = TCDBmainwks.cell(
            (matchTitleRow[0], resultcol)
        ).value  # some string has duplicate translate
        await ctx.send(message)
        if not name.isascii():  # chinese to english
            searchstr = message.replace(" ", "+")
            guideurl = "<https://orna.guide/search?searchstr=" + searchstr + ">"
            await ctx.send(guideurl)

    @commands.command(
        name="subscribe",
        help="使用方法: ~subscribe | 使中文機器人監聽此頻道的圖片並嘗試辨識",
    )
    async def subscribe(self, ctx, *args):
        channelmatrix = imgporcesschannels.get_all_values(
            returnas="cell",
            majdim="ROWS",
            include_tailing_empty=False,
            include_tailing_empty_rows=False,
        )[1::]
        otherregistered = False
        for pair in channelmatrix:
            if (
                str(ctx.guild.id) == pair[0].value
                and str(ctx.channel.id) == pair[1].value
            ):
                await ctx.send("本頻道已註冊過，無須再進行註冊")
                return
            elif (
                str(ctx.guild.id) == pair[0].value
                and str(ctx.channel.id) != pair[1].value
            ):
                otherregistered = True
        imgporcesschannels.insert_rows(
            1, values=[str(ctx.guild.id), str(ctx.channel.id)]
        )
        if otherregistered:
            await ctx.send("成功註冊本頻道，偵測到其他頻道也有註冊\n若其他頻道轉為其他用途，記得使用~unsubscribe退出監聽頻道")
        else:
            await ctx.send("成功註冊本頻道，請注意10秒後機器人才會開始監聽本頻道")

    @commands.command(
        name="unsubscribe",
        help="使用方法: ~unsubscribe | 移除中文機器人對此頻道的監聽",
    )
    async def unsubscribe(self, ctx, *args):
        channelmatrix = imgporcesschannels.get_all_values(
            returnas="cell",
            majdim="ROWS",
            include_tailing_empty=False,
            include_tailing_empty_rows=False,
        )
        for pair in channelmatrix:
            if (
                str(ctx.guild.id) == pair[0].value
                and str(ctx.channel.id) == pair[1].value
            ):
                imgporcesschannels.delete_rows(pair[0].row)
                await ctx.send("已移除本頻道，可使用~subscribe再次訂閱")
                return

    async def img_process(self, ctx):
        issubscribe = False
        for pair in self.imgporcesschannellist:
            if pair[0] == str(ctx.guild.id):
                if pair[1] == str(ctx.channel.id):
                    issubscribe = True
        if not issubscribe:
            return
        if time.time() - self.updatetime > 10:
            self.imgporcesschannellist = imgporcesschannels.get_all_values(
                returnas="matrix",
                majdim="ROWS",
                include_tailing_empty=False,
                include_tailing_empty_rows=False,
            )[1::]
            self.updatetime = time.time()
        for att in ctx.attachments:
            attname = att.content_type.split("/")[1]
            if attname not in IMAGE_TYPE:
                return
            textlist = self.img_text_detection_with_url(att.url)
            if not textlist:  # sometims google can't access the url
                file = await att.read()
                textlist = self.img_text_detection_with_file(file)
            if not textlist:
                await ctx.reply("無法辨識圖片中的文字")
            translated_strs = self.img_text_translate(textlist)

            searchstr = (
                "%assess "
                + translated_strs["itemnamestr"]
                + translated_strs["levelstr"]
                + translated_strs["statstr"]
            )
            searchstr = searchstr.replace("\n", " ")
            searchstr = searchstr.replace("  ", " ")
            await ctx.reply(searchstr)

    def img_text_detection_with_url(self, url):
        image = vision.Image()
        image.source.image_uri = url
        response = visionclient.text_detection(image=image)
        if "text_annotations" not in response:
            print("Google API error:", response.error)  # logging
            return
        textlist = response.text_annotations[0].description.split("\n")
        return textlist

    def img_text_detection_with_file(self, file):
        image = vision.Image(content=file)
        response = visionclient.text_detection(image=image)
        if "text_annotations" not in response:
            print("Google API error: ", response.error)  # logging
            return
        textlist = response.text_annotations[0].description.split("\n")
        return textlist

    def img_text_translate(self, textlist):
        untrans_itemnamestr = ""
        levelstr = ""
        statstr = ""
        for textindex in range(0, len(textlist)):
            if textlist[textindex] == "裝飾品":
                break
            if textlist[textindex] == "儲藏室":
                untrans_itemnamestr = textlist[textindex + 1]
                if untrans_itemnamestr.startswith("*"):
                    # sometimes Adornment slot will being detect as "*"s
                    untrans_itemnamestr = textlist[textindex + 2]
            elif textlist[textindex].startswith("等級"):
                levelstr = textlist[textindex]
                levelstr = levelstr.replace(" ", "")
                levelstr = levelstr.replace("等級", "")
                levelstr = " (" + levelstr + ") "
            elif any(keyword in textlist[textindex] for keyword in MATCH_WORD_TC):
                statstr += textlist[textindex]
        if not untrans_itemnamestr:
            return  # can't find chinese keyword in the image, quit process
        allmatchTitleRow = []
        data = TCDBmainwks.get_col(3, returnas="cell", include_tailing_empty=False)[2::]
        strindex = len(untrans_itemnamestr) - 1
        while strindex >= 0:  # loop search DB using [-1::],[-2::].....[0::]
            matchTitleRow = [
                title.row
                for title in data
                if title.value.lower() == untrans_itemnamestr[strindex::]
            ]
            allmatchTitleRow.extend(matchTitleRow)
            strindex -= 1
        itemnamestrindex = allmatchTitleRow[-1]  # max len match string
        if not levelstr:
            levelstr = " (1) "
        for TCstr, ENstr in zip(MATCH_WORD_TC, MATCH_WORD_EN):
            statstr = statstr.replace(" ", "")
            statstr = statstr.replace(TCstr, ENstr)
            statstr = statstr.replace(",", "")  # 1,234 to 1234
        itemnamestr = TCDBmainwks.cell((itemnamestrindex, 2)).value
        return {"itemnamestr": itemnamestr, "levelstr": levelstr, "statstr": statstr}

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.attachments:
            await self.img_process(ctx)


def setup(bot):
    bot.add_cog(Orna(bot))