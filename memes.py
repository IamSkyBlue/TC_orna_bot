from PIL import Image, ImageFont, ImageDraw
import uuid
import discord
from discord.ext import commands, tasks


class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="fightjpg", help='使用方法: ~fightjpg "第一格句子" "第二".....總共五個 中間記得空格'
    )
    async def fightjpg(self, ctx, *args):
        textheight = 300
        textlist = args
        img = Image.open("./src/imgs/origin.png")
        fontpath = "./src/fonts/TaipeiSansTCBeta-Bold.ttf"
        font = ImageFont.truetype(fontpath, 40)
        draw = ImageDraw.Draw(img)
        imgwidth = img.size[0]
        for text in textlist:
            width = draw.textsize(text, font=font)[0]
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