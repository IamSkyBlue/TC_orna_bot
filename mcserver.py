import os
import requests
import json
import discord
from discord.ext import commands, tasks
from mcstatus import MinecraftServer


ALLOW_GUILD = eval(os.getenv("ALLOW_GUILD"))

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": os.getenv("DIGITALOCEAN_API_TOKEN"),
}

URL = "https://api.digitalocean.com/v2/droplets/" + os.getenv(
    "DIGITALOCEAN_DROPLETS_ID"
)

SERVER_IP = os.getenv("MC_SERVER_IP")
server = MinecraftServer.lookup(SERVER_IP)


class MCserver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mc-status", help="伺服器狀態 使用方法: ~mc-status")
    async def mcstatus(self, ctx, *args):
        if not ctx.guild.id in ALLOW_GUILD:
            await ctx.send("這是私人的伺服器喔~抱歉")
            return
        response = requests.get(URL, headers=HEADERS)
        if response.status_code != 200:
            await ctx.send("發生問題，請聯絡SkyBlue")
            await ctx.send(str(response.content))
        else:
            status = json.loads(response.content)
            if status["droplet"]["status"] == "off":
                await ctx.send("伺服器是關閉狀態")
            elif status["droplet"]["status"] == "active":
                try:
                    query = server.query()
                    onlinePeople = "\n".join(query.players.names)
                except:
                    await ctx.send("目前伺服器正在開啟中喔，如果已經等很久還沒開好請聯絡SkyBlue")
                    return
                await ctx.send("伺服器開著喔")
                if query.players.names:
                    await ctx.send("目前有這些人在線上:\n" + onlinePeople)
                else:
                    await ctx.send("但沒有人在線上QQ")
            else:
                await ctx.send("發生問題，請聯絡SkyBlue")
                await ctx.send(str(response.content))

    @commands.command(name="mc-on", help="開啟伺服器 使用方法: ~mc-on")
    async def mcon(self, ctx, *args):
        if not ctx.guild.id in ALLOW_GUILD:
            await ctx.send("這是私人的伺服器喔~抱歉")
            return
        response = requests.get(URL, headers=HEADERS)
        if response.status_code != 200:
            await ctx.send("發生問題，請聯絡SkyBlue")
            await ctx.send(str(response.content))
        else:
            status = json.loads(response.content)
            if status["droplet"]["status"] == "active":
                try:
                    status = server.status()
                    await ctx.send("伺服器開著喔，直接加入就可以了")
                except:
                    await ctx.send("伺服器還在開啟當中，如果已經等很久還沒開好請聯絡SkyBlue")
            else:
                payload = {"type": "power_on"}
                response = requests.post(
                    URL + "/actions", data=json.dumps(payload), headers=HEADERS
                )
                if response.status_code == 201:
                    await ctx.send("伺服器開啟中，請稍等~\n如果等等沒有要繼續玩了記得關掉伺服器喔")
                else:
                    await ctx.send("發生問題，請聯絡SkyBlue")
                    await ctx.send(str(response.content))

    @commands.command(name="mc-off", help="關閉伺服器 使用方法: ~mc-off")
    async def mcoff(self, ctx, *args):
        if not ctx.guild.id in ALLOW_GUILD:
            await ctx.send("這是私人的伺服器喔~抱歉")
            return
        response = requests.get(URL, headers=HEADERS)
        if response.status_code != 200:
            await ctx.send("發生問題，請聯絡SkyBlue")
            await ctx.send(str(response.content))
        else:
            status = json.loads(response.content)
            if status["droplet"]["status"] == "off":
                await ctx.send("伺服器已經是關閉狀態")
            elif status["droplet"]["status"] == "active":
                try:
                    query = server.query()
                    if query.players.names:
                        await ctx.send("伺服器裡還有人喔，請大家都退出才可以關伺服器喔")
                    else:
                        payload = {"type": "shutdown"}
                        response = requests.post(
                            URL + "/actions", data=json.dumps(payload), headers=HEADERS
                        )
                        if response.status_code == 201:
                            await ctx.send("正在關閉伺服器，如果要再開啟請稍待片刻再啟動")
                        else:
                            await ctx.send("發生問題，請聯絡SkyBlue")
                            await ctx.send(str(response.content))
                except:
                    await ctx.send("伺服器還在開啟當中，先不要急著關\n如果已經等很久還沒開好請聯絡SkyBlue")
            else:
                await ctx.send("發生問題，請聯絡SkyBlue")
                await ctx.send(str(response.content))
