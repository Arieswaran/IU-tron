import discord
import os
from discord.ext import commands
from discord import ButtonStyle
from Helpers import AIHelper, ClickupHelper, AppHelper
from Views import DuplicateTask, ClickupTask

game_name = "Hitwicket Superstars"  # change this to your game name

token = os.getenv("DISCORD_NATASHA_TOKEN_2")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=["n", "N"], help_command=None, case_insensitive=True, intents=intents)


@bot.event
async def on_ready():
    activity = discord.Activity(
        type=discord.ActivityType.playing, name=game_name)
    await bot.change_presence(activity=activity)
    print("We have logged in as {0.user}".format(bot))


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    if message.mention_everyone:
        return
    if message.author.bot:
        await AppHelper.check_and_post_reviews(message, bot)
        return
    ctx = await bot.get_context(message)
    is_cmd = ctx.valid
    if (is_cmd):
        await bot.process_commands(message)
    elif bot.user.mentioned_in(message):
        message.content = message.content.replace(bot.user.mention, "")
        if message.reference is not None:
            if bot.user.mentioned_in(message.reference.resolved):
                return
            if message.reference.resolved.author == bot.user:
                return
            message.content = message.reference.resolved.content
            message.attachments = message.reference.resolved.attachments
        if message.content == "" and len(message.attachments) == 0:
            await ctx.reply("Please provide a message to make a task for")
            return

        title = ""
        if message.content != "":
            title = AIHelper.getTaskTitle(message.content)
        if title is None:
            await ctx.reply("OpenAI API failed to generate a title for the task. Please try again later")
            return
        similar_tasks = []
        all_tasks = ClickupHelper.getAllTasks()
        for task in all_tasks:
            if AppHelper.similarity_check(task.name, title, 0.8):
                similar_tasks.append(task)

        if len(similar_tasks) > 0:
            view = DuplicateTask(message, title, message.content, message.attachments)
            embed = discord.Embed(title="Duplicate Tasks",
                                  description="The following tasks are similar to the one you are trying to create. Do you still want to create a new task?",
                                  color=0x00ff00)
            for task in similar_tasks:
                embed.add_field(name=task.name, value=task.url, inline=False)
            await ctx.reply(embed=embed, view=view)
            return

        description = ""
        if message.content != "":
            description = AIHelper.getTaskDescription(message.content)
        attachment_links = [attachment.url for attachment in message.attachments]
        if len(attachment_links) > 0:
            description = description + "\n\nAttachments:\n" + "\n".join(attachment_links)
        task = ClickupHelper.createTask(title, description)
        if task is None:
            await ctx.reply("Clickup API failed to create a task. Please try again later")
            return
        view = ClickupTask(task)
        embed = discord.Embed(title=task.name, description=task.description, color=0x00ff00)
        embed.add_field(name="Status", value=task.status.status, inline=True)
        embed.add_field(name="Priority", value="None", inline=True)  # hack
        view.add_item(discord.ui.Button(label="Open in Clickup", style=ButtonStyle.link, url=task.url))
        await ctx.reply(embed=embed, view=view)




# command error
@bot.event
async def on_command_error(ctx, error):
    return  # will remove if we add commands later


@commands.command()
async def config(self, ctx):
    print("TODO")


class ConfigView(discord.ui.View):
    def _init_(self):
        super()._init_()


bot.run(token)
