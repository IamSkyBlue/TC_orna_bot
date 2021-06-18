# encoding: utf-8
import os
import traceback

import discord
from discord.ext import commands, tasks

from orna import Orna
from poll import Poll
from mcserver import MCserver
from memes import Memes

token = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(
    command_prefix="~", description="本來是Orna字典機器人,但現在已經是參雜其他我自己要用的功能的機器人了"
)

bot.load_extension("orna")
bot.load_extension("ornaimg")
bot.load_extension("poll")
bot.load_extension("memes")

bot.load_extension(
    "mcserver"
)  # this cog is for private use! If you fork from this repo, you can delete this line


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing, name="~help 前綴是波浪符!"
        )
    )
    print("connected to Discord!")


@bot.event
async def on_error(event, *args, **kwargs):
    print(traceback.format_exc())


@bot.command()
async def msgsend(ctx, msg, channelid: int):
    if ctx.author.id in eval(os.getenv("STAFF_ID")):
        channel = bot.get_channel(channelid)
        await channel.send(msg)


@bot.command()
async def msgreply(ctx, msg, channelid: int, msgid: int):
    if ctx.author.id in eval(os.getenv("STAFF_ID")):
        channel = bot.get_channel(channelid)
        message = await channel.fetch_message(msgid)
        await message.reply(msg)


bot.run(token)