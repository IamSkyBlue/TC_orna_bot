# encoding: utf-8
import os
import traceback

import discord
from discord.ext import commands, tasks

from orna import Orna
from poll import Poll
from mcserver import MCserver
from memes import Memes
from help import TCHelp

token = os.getenv("DISCORD_TOKEN")
STAFF_IDS = eval(os.getenv("STAFF_ID"))
bot = commands.Bot(
    command_prefix="~",
    description="台灣社群Orna字典機器人",
    owner_ids=STAFF_IDS,
    help_command=TCHelp(),
)

bot.load_extension("orna")
bot.load_extension("ornaimg")
bot.load_extension("poll")
bot.load_extension("memes")
bot.load_extension("admin")


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


bot.run(token)