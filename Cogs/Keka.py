import datetime
import discord
from discord.ext import commands, tasks

ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
time = datetime.time(hour=18, minute=22, tzinfo=ist)


class Keka(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.emoji = "🤡"
        self.invisible = False
        #self.keka_loop.start()


    @tasks.loop(time=time)
    async def keka_loop(self):
        await self.bot.wait_until_ready()
        print("IU")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Keka(bot))
