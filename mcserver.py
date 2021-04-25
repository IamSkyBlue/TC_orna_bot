import os
import requests
import socket
import json
import time
from datetime import datetime

import discord
from discord.ext import commands, tasks
from mcstatus import MinecraftServer


ALLOW_GUILD = eval(os.getenv("ALLOW_GUILD"))

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": os.getenv("DIGITALOCEAN_API_TOKEN"),
}

SSH_KEYS = eval(os.getenv("SSH_KEYS"))


class Droplet:
    def __init__(self):
        self.id = ""
        self.status = ""
        self.ip_address = ""
        self.update()

    def update(self):
        url = "https://api.digitalocean.com/v2/droplets?page=1&per_page=2"
        response = requests.get(url, headers=HEADERS)
        content = json.loads(response.content)
        if not content["droplets"]:
            self.id = ""
            self.status = ""
            self.ip_address = ""
            return
        else:
            self.id = content["droplets"][0]["id"]
            self.status = content["droplets"][0]["status"]
            for address in content["droplets"][0]["networks"]["v4"]:
                if address["type"] == "private":
                    continue
                else:
                    self.ip_address = address["ip_address"]
            return

    def get_id(self):
        self.update()
        return self.id

    def get_status(self):
        self.update()
        return self.status

    def get_address(self):
        self.update()
        return self.ip_address

    def shutdown_and_make_snapshot_and_delete(self):
        self.update()
        url = (
            "https://api.digitalocean.com/v2/droplets/"
            + str(self.get_id())
            + "/actions"
        )
        payload = {"type": "shutdown"}
        response = requests.post(url, data=json.dumps(payload), headers=HEADERS)
        content = json.loads(response.content)
        action = content["action"]["id"]
        url = "https://api.digitalocean.com/v2/actions/" + str(action)
        counter = 1
        while True:
            response = requests.get(url, headers=HEADERS)
            content = json.loads(response.content)
            if content["action"]["status"] == "completed":
                break
            elif counter > 120:
                return False
            else:
                counter += 1
                time.sleep(5)

        url = (
            "https://api.digitalocean.com/v2/droplets/"
            + str(self.get_id())
            + "/actions"
        )
        payload = {
            "type": "snapshot",
            "name": "SkyLand_Snapshot_" + datetime.now().strftime("%Y-%m-%d--%H-%M-%S"),
        }
        response = requests.post(url, data=json.dumps(payload), headers=HEADERS)
        content = json.loads(response.content)
        action = content["action"]["id"]
        url = "https://api.digitalocean.com/v2/actions/" + str(action)
        counter = 1
        while True:
            response = requests.get(url, headers=HEADERS)
            content = json.loads(response.content)
            if content["action"]["status"] == "completed":
                break
            elif counter > 60:
                return False
            else:
                counter += 1
                time.sleep(10)

        url = "https://api.digitalocean.com/v2/droplets/" + str(self.get_id())
        response = requests.delete(url, headers=HEADERS)
        if response.status_code == 204:
            return True
        else:
            return False


class Snapshot:
    def __init__(self):
        self.id = ""
        self.update()

    def update(self):
        url = "https://api.digitalocean.com/v2/snapshots?page=1&per_page=100&resource_type=droplet"
        response = requests.get(url, headers=HEADERS)
        content = json.loads(response.content)
        if not content["snapshots"]:
            self.id = ""
            return
        else:
            self.id = content["snapshots"][-1]["id"]
            return

    def get_id(self):
        self.update()
        return self.id

    def create_droplet(self):
        self.update()
        url = "https://api.digitalocean.com/v2/droplets"
        payload = {
            "name": "SkyLandServer",
            "region": "sgp1",
            "size": "s-2vcpu-4gb",
            "image": self.id,
            "ssh_keys": SSH_KEYS,
        }
        response = requests.post(url, data=json.dumps(payload), headers=HEADERS)
        if response.status_code == 202:
            return True
        else:
            return False


def get_server():
    server = MinecraftServer.lookup(droplet.get_address() + ":25565")
    return server


droplet = Droplet()
snapshot = Snapshot()


class MCserver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mc-status", help="伺服器狀態 使用方法: ~mc-status")
    async def mc_status(self, ctx, *args):
        if ctx.guild.id not in ALLOW_GUILD:
            await ctx.send("這是私人的伺服器喔~抱歉")
            return
        if not droplet.get_id():
            await ctx.send("伺服器是關閉狀態")
            return
        else:
            try:
                server = get_server()
                query = server.query()
                online_people = "\n".join(query.players.names)
            except socket.timeout:
                await ctx.send("目前伺服器正在開啟中喔，如果已經等很久還沒開好請聯絡SkyBlue")
                return
            except Exception as e:
                await ctx.send("發生問題，請聯絡SkyBlue" + str(e))
                return
            await ctx.send("伺服器開著喔 IP: " + droplet.get_address() + ":25565")
            if query.players.names:
                await ctx.send("目前有這些人在線上:\n" + online_people)
            else:
                await ctx.send("但沒有人在線上QQ")

    @commands.command(name="mc-on", help="開啟伺服器 使用方法: ~mc-on")
    async def mc_on(self, ctx, *args):
        if ctx.guild.id not in ALLOW_GUILD:
            await ctx.send("這是私人的伺服器喔~抱歉")
            return
        if droplet.get_id():
            try:
                server = get_server()
                status = server.status()
                await ctx.send("伺服器開著喔，直接加入就可以了")
            except socket.timeout:
                await ctx.send("伺服器還在開啟當中，如果已經等很久還沒開好請聯絡SkyBlue")
                return
            except Exception as e:
                await ctx.send("發生問題，請聯絡SkyBlue" + str(e))
                return
        else:
            success = snapshot.create_droplet()
            if success:
                await ctx.send("伺服器開啟中，啟動完成會有訊息，請稍等~")
                counter = 1
                while True:
                    try:
                        counter += 1
                        time.sleep(10)
                        server = get_server()
                        status = server.status()
                        break
                    except Exception as e:
                        if counter > 60:
                            await ctx.send("發生問題，請聯絡SkyBlue")
                            return
                        else:
                            continue
                await ctx.send(
                    "伺服器已開啟完成\n如果等等沒有要繼續玩了記得關掉伺服器喔\n伺服器IP為: "
                    + droplet.get_address()
                    + ":25565"
                )
            else:
                await ctx.send("發生問題，請聯絡SkyBlue")

    @commands.command(name="mc-off", help="關閉伺服器 使用方法: ~mc-off")
    async def mc_off(self, ctx, *args):
        if ctx.guild.id not in ALLOW_GUILD:
            await ctx.send("這是私人的伺服器喔~抱歉")
            return
        if not droplet.get_id():
            await ctx.send("伺服器已經是關閉狀態")
        else:
            try:
                server = get_server()
                query = server.query()
                if query.players.names:
                    await ctx.send("伺服器裡還有人喔，請大家都退出才可以關伺服器喔")
                else:
                    await ctx.send("正在關閉伺服器，如果要再開啟請稍待成功關閉訊息出現後再開啟")
                    success = droplet.shutdown_and_make_snapshot_and_delete()
                    if success:
                        await ctx.send("成功關閉伺服器")
                    else:
                        await ctx.send("發生問題，請聯絡SkyBlue")
            except socket.timeout:
                await ctx.send("伺服器還在開啟當中，先不要急著關\n如果已經等很久還沒開好請聯絡SkyBlue")
                return
            except Exception as e:
                await ctx.send("發生問題，請聯絡SkyBlue" + str(e))
                return
