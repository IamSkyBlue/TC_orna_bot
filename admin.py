import discord
from discord.ext import commands, tasks


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="msgsend", hidden=True)
    @commands.is_owner()
    async def msgsend(self, _, msg: str, channelid: int):
        try:
            channel = self.bot.get_channel(channelid)
            await channel.send(msg)
        except Exception as e:
            await self.bot.say("\N{PISTOL}")
            await self.bot.say("{}: {}".format(type(e).__name__, e))
        else:
            await self.bot.say("\N{OK HAND SIGN}")

    @commands.command(name="msgreply", hidden=True)
    @commands.is_owner()
    async def msgreply(self, _, msg: str, channelid: int, msgid: int):
        try:
            channel = self.bot.get_channel(channelid)
            message = await channel.fetch_message(msgid)
            await message.reply(msg)
        except Exception as e:
            await self.bot.say("\N{PISTOL}")
            await self.bot.say("{}: {}".format(type(e).__name__, e))
        else:
            await self.bot.say("\N{OK HAND SIGN}")

    @commands.command(hidden=True)
    async def load(self, ctx, *, module):
        """Loads a module."""
        try:
            self.bot.load_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f"{e.__class__.__name__}: {e}")
        else:
            await ctx.send("\N{OK HAND SIGN}")

    @commands.command(hidden=True)
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f"{e.__class__.__name__}: {e}")
        else:
            await ctx.send("\N{OK HAND SIGN}")

    @commands.command(name="reload", hidden=True)
    async def _reload(self, ctx, *, module):
        """Reloads a module."""
        try:
            self.bot.reload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f"{e.__class__.__name__}: {e}")
        else:
            await ctx.send("\N{OK HAND SIGN}")


def setup(bot):
    bot.add_cog(Admin(bot))