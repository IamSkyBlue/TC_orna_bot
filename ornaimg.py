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

OrnaTCDB = gc.open("OrnaTCDB")
TCDBmainwks = OrnaTCDB[0]
imgporcesschannels = OrnaTCDB[1]
correctionsheet = OrnaTCDB[2]

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
    "暴擊:",
    "+視線範圍",
    "-視線範圍",
    "+經驗加成",
    "-經驗加成",
    "+金幣加成",
    "-金幣加成",
    "+歐幣加成",
    "-歐幣加成",
    "+幸運加成",
    "-幸運加成",
    "+跟隨者行動",
    "-跟隨者行動",
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
    "",
    "",
    "",
    "",
)


class Ornaimg(commands.Cog):
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
                return
            translated_strs = self.img_find_strings(textlist, False)
            print("translated_strs: ", translated_strs)
            if translated_strs["untrans_itemnamestr"] == "":
                translated_strs = self.img_find_strings(textlist, True)
            if translated_strs["untrans_itemnamestr"] == "":
                # if first try and second try all failed at this point
                # this mean the img is not game screenshot
                await ctx.reply('無法辨識圖片中的物品名稱，截圖請勿擋住左上角的"儲藏室"')
                return
            if translated_strs["israndom"]:
                await ctx.reply("ornabot無法辨識隨機產生的物品")
                return
            if not translated_strs["istranslated"]:
                # the itemname need translation only if it is chinese
                itemnamestr = self.translate_correction(
                    translated_strs["untrans_itemnamestr"]
                )
                itemnamestr = self.img_text_translate(itemnamestr)
            else:
                itemnamestr = ""
            levelstatstr = translated_strs["levelstr"] + translated_strs["statstr"]
            levelstatstr = levelstatstr.replace("\n", " ")
            levelstatstr = levelstatstr.replace("  ", " ")
            if not itemnamestr:
                # if img_text_translate return an empty string
                # this mean the name of the item can not be found in the ornaTCDB
                if translated_strs["istranslated"]:
                    await ctx.reply("英文物品名稱: " + translated_strs["untrans_itemnamestr"])
                    await ctx.channel.send("本機器人非設計給原本就是英文名稱的物品，請將介面語言切換成英文直接使用ornabot")
                else:
                    await ctx.reply(
                        "無法在資料庫中找到相符物品: " + translated_strs["untrans_itemnamestr"]
                    )
                    await ctx.channel.send("可能是隨機產生的物品或是辨識錯字，若是錯字請聯繫 @SkyBlue#1688")
                await ctx.channel.send(
                    "數值字串: " + translated_strs["levelstr"] + translated_strs["statstr"]
                )
                return
            searchstr = "%assess " + itemnamestr + levelstatstr
            await ctx.reply(searchstr)
            if translated_strs["hasadornment"]:
                await ctx.channel.send("偵測到有寶石鑲嵌，請自行扣除寶石所增加的數值後再貼上")

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

    def img_find_strings(self, textlist, secondtry: bool):
        untrans_itemnamestr = ""
        levelstr = ""
        statstr = ""
        hasadornment = False
        israndom = False
        istranslated = False
        for textindex in range(0, len(textlist)):
            if textlist[textindex] == "裝飾品":
                hasadornment = True
                break
            if "隨機產生" in textlist[textindex]:
                israndom = True
                break
            if textlist[textindex] == "儲藏室":
                if (
                    secondtry
                ):  # main itemnamestr translation failed, try to use itemname on top left of the screen
                    untrans_itemnamestr = textlist[textindex - 1]
                else:
                    untrans_itemnamestr = textlist[textindex + 1]
                    indexcount = 0
                    while (
                        untrans_itemnamestr[0].isascii()
                        or len(untrans_itemnamestr) < 2
                        or untrans_itemnamestr.startswith(("中", "回"))
                    ):
                        if (
                            len(untrans_itemnamestr) > 10
                            and untrans_itemnamestr.isascii()
                            and not untrans_itemnamestr.startswith(("OO", "oo", "00"))
                        ):
                            # the item name is already english
                            istranslated = True
                            break
                        indexcount += 1
                        # sometimes Adornment slot or item img will being detect as texts
                        untrans_itemnamestr = textlist[textindex + 1 + indexcount]

            elif textlist[textindex].startswith("等級"):
                levelstr = textlist[textindex]
                levelstr = levelstr.replace(" ", "")
                levelstr = levelstr.replace("等級", "")
                levelstr = " (" + levelstr + ") "
            elif any(keyword in textlist[textindex] for keyword in MATCH_WORD_TC):
                statstr += textlist[textindex]
        if not levelstr:
            levelstr = " (1) "
        statstr = statstr.replace(" ", "")
        statstr = statstr.replace(",", "")  # 1,234 to 1234
        statstr = statstr.replace("—", "-")
        statstr = statstr.replace("o", "0")
        statstr = statstr.replace("O", "0")
        for TCstr, ENstr in zip(MATCH_WORD_TC, MATCH_WORD_EN):
            statstr = statstr.replace(TCstr, ENstr)

        return {
            "untrans_itemnamestr": untrans_itemnamestr,
            "levelstr": levelstr,
            "statstr": statstr,
            "hasadornment": hasadornment,
            "israndom": israndom,
            "istranslated": istranslated,
        }

    def img_text_translate(self, untrans_itemnamestr):
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
        if len(allmatchTitleRow) > 1:
            itemnamestrindex = allmatchTitleRow[-1]  # max len match string
        elif len(allmatchTitleRow) == 0:
            return
        else:
            itemnamestrindex = allmatchTitleRow[0]
        itemnamestr = TCDBmainwks.cell((itemnamestrindex, 2)).value
        return itemnamestr

    def translate_correction(self, itemstring):
        correctionlist = correctionsheet.get_all_values(
            returnas="matrix",
            majdim="ROWS",
            include_tailing_empty=False,
            include_tailing_empty_rows=False,
        )[1::]
        for pair in correctionlist:
            itemstring = itemstring.replace(pair[0], pair[1])
        return itemstring

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.attachments:
            await self.img_process(ctx)


def setup(bot):
    bot.add_cog(Ornaimg(bot))