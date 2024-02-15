from PIL import Image, ImageFont, ImageDraw
import uuid
import discord
from discord.ext import commands, tasks


class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="fightjpg",
        help='使用方法: ~fightjpg "第一格句子" "第二".....總共五個 中間記得空格',
        brief="產生迷因圖片",
    )
    async def fightjpg(self, ctx, *args):
        if len(args) != 5:
            await ctx.send("創建失敗，請輸入剛好5個句子")
            return
        textheight = 300
        textlist = args
        img = Image.open("./src/imgs/origin.png")
        fontpath = "./src/fonts/TaipeiSansTCBeta-Bold.ttf"
        font = ImageFont.truetype(fontpath, 40)
        draw = ImageDraw.Draw(img)
        imgwidth = img.size[0]
        for text in textlist:
            width = draw.textlength(text, font=font)
            draw.text(
                ((imgwidth - width) / 2, textheight),
                text,
                font=font,
                fill=(255, 255, 255),
            )
            textheight += 360
        newimgname = str(uuid.uuid4()) + ".png"
        img.save(newimgname)
        await ctx.send(file=discord.File(newimgname))


async def setup(bot):
    await bot.add_cog(Memes(bot))