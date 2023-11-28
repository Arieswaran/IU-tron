import discord
from discord.ext import commands, tasks

class Keka(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.emoji = "🤡"
        self.invisible = False
        self.keka_loop.start()

    @commands.command()
    async def keka(self, ctx: commands.Context):
        """Keka"""
        await ctx.reply("Keka")

    @tasks.loop(seconds=5)
    async def keka_loop(self):
        await self.bot.wait_until_ready()
        print("IU")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Keka(bot))