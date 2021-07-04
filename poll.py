import discord
from discord.ext import commands, tasks


class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="poll",
        help='使用方法: ~poll "投票名稱" "項目一" "項目二"..... 中間記得空格',
        brief="創建投票",
    )
    async def poll(self, ctx, *args):
        emojiLetters = [
            "\N{REGIONAL INDICATOR SYMBOL LETTER A}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER B}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER C}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER D}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER E}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER F}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER G}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER H}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER I}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER J}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER K}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER L}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER M}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER N}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER O}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER P}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER Q}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER R}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER S}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER T}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER U}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER V}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER W}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER X}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER Y}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER Z}",
        ]
        if len(args) > 27:
            await ctx.send("創建失敗，請勿超過26個選項")
            return
        if len(args) == 1:
            await ctx.send("創建失敗，至少要有1個選項")
            return
        await ctx.send("\N{Bar Chart} **" + args[0] + "**")
        optionMessage = ""
        for i, item in enumerate(args[1::]):
            optionMessage = optionMessage + emojiLetters[i] + " " + item + "\n"
        embed = discord.Embed(description=optionMessage, color=0x0000E1)
        pollMessage = await ctx.send(embed=embed)
        for i, item in enumerate(args[1::]):
            await pollMessage.add_reaction(emojiLetters[i])


def setup(bot):
    bot.add_cog(Poll(bot))