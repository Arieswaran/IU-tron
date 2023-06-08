import requests
import discord
import pyclickup
import os
from discord.ext import commands
from discord import ButtonStyle
from discord.ui import Button
import enum
import openai
import Levenshtein
import time

game_name = "Hitwicket Superstars" #change this to your game name

token = os.getenv("DISCORD_NATASHA_TOKEN")
#get read messages and send messages permissions
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=["n","N"],help_command=None, case_insensitive = True, intents=intents)
openai.api_key = os.getenv("OPENAI_API_KEY")
#clickup
clickup_token = os.getenv("CLICKUP_TOKEN")
clickup = pyclickup.ClickUp(clickup_token)
main_team = clickup.teams[0]
main_space = main_team.spaces[0]
main_project = main_space.projects[2]
bug_list = main_project.lists[1]
statuses_list = main_project.statuses
all_tasks = bug_list.get_all_tasks()

def updateAllTasks():
    global all_tasks
    all_tasks = bug_list.get_all_tasks()

def getTask(task_id):
    for task in all_tasks:
        if task.id == task_id:
            return task
    return None

def createTask(name, description):
    task = bug_list.create_task(name, description)
    updateAllTasks()
    return getTask(task)


def getTaskTitle(message):
    retries = 0
    while retries < 5:
        try:
            a = "Make a clickup task title less than 13 words for the below message\n"
            a = a + message
            res = openai.Completion.create(
                model="text-davinci-003",
                prompt=a,
                max_tokens=512,
                temperature=0
            )
            return "[BUG] "+ res["choices"][0]["text"].strip()
        except:
            retries = retries + 1
            time.sleep(1)
    return None

def getTaskDescription(message):
    retries = 0
    while retries < 5:
        try:
            a = "Make a bug report for the below message for a mobile cricket game\n"
            a = a + message
            res = openai.Completion.create(
                model="text-davinci-003",
                prompt=a,
                max_tokens=1000,
                temperature=0
            )
            return res["choices"][0]["text"].strip()
        except:
            retries = retries + 1
            time.sleep(1)
    return None


def similarity_check(title1, title2, threshold):
    lev_similarity = Levenshtein.ratio(title1, title2)
    title1_words = set(title1.split())
    title2_words = set(title2.split())
    jac_similarity = len(title1_words & title2_words) / \
        len(title1_words | title2_words)
    if lev_similarity >= threshold or jac_similarity >= threshold:
        return True
    else:
        return False

class Priority(enum.Enum):
    """task priority enum"""

    NONE = 0
    URGENT = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@bot.event
async def on_ready():
    activity = discord.Activity(
        type=discord.ActivityType.playing, name=game_name)
    await bot.change_presence(activity=activity)
    print("We have logged in as {0.user}".format(bot))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.mention_everyone:
        return
    if message.author.bot:
        if (message.channel.id == 1116309975392849950): # original channel where all app follow reviews are posted
            embed = message.embeds[0]
            msg = embed.description
            msg = msg.split("Hitwicket Cricket Games")[1].strip()
            rating, title, description = msg.split("\n")
            by = embed.fields[0].value
            if (len(description.split(" ")) > 4 or len(description) > 20): # filter out reviews with less than 4 words in description or less than 20 characters
                channel = bot.get_channel(1070598072104656906) # channel where we want to post the filtered reviews
                embed = discord.Embed(
                    title=title, description=rating + "\n" + description + "\n" + by)
                await channel.send(embed=embed)
        return
    ctx = await bot.get_context(message)
    is_cmd = ctx.valid
    if(is_cmd):
        await bot.process_commands(message)
    elif bot.user.mentioned_in(message):
        message.content = message.content.replace(bot.user.mention, "")
        if message.reference != None:
            if(bot.user.mentioned_in(message.reference.resolved)):
                return
            if(message.reference.resolved.author == bot.user):
                return
            message.content = message.reference.resolved.content
            message.attachments = message.reference.resolved.attachments
        if message.content == "" and len(message.attachments) == 0:
            await ctx.reply("Please provide a message to make a task for")
            return
            
        title = ""
        if(message.content != ""):
            title = getTaskTitle(message.content)
        if title == None:
            await ctx.reply("OpenAI API failed to generate a title for the task. Please try again later")
            return
        similar_tasks = []
        for task in all_tasks:
            if(similarity_check(task.name, title, 0.8)):
                similar_tasks.append(task)
        
        if(len(similar_tasks) > 0):
            view = DuplicateTask(message,title,message.content,message.attachments)
            embed = discord.Embed(title="Duplicate Tasks", description="The following tasks are similar to the one you are trying to create. Do you still want to create a new task?", color=0x00ff00)
            for task in similar_tasks:
                embed.add_field(name=task.name, value=task.url, inline=False)
            await ctx.reply(embed=embed,view = view)
            return
        
        description = ""
        if(message.content != ""):
            description = getTaskDescription(message.content)
        attachement_links = [attachement.url for attachement in message.attachments]
        if(len(attachement_links) > 0):
            description = description + "\n\nAttachments:\n" + "\n".join(attachement_links)
        task = createTask(title, description)
        if task == None:
            await ctx.reply("Clickup API failed to create a task. Please try again later")
            return
        view = ClickupTask(task)
        embed = discord.Embed(title=task.name, description=task.description, color=0x00ff00)
        embed.add_field(name="Status", value=task.status.status, inline=True)
        embed.add_field(name="Priority", value= "None", inline=True) #hack
        view.add_item(discord.ui.Button(label="Open in Clickup",style=ButtonStyle.link,url=task.url))
        await ctx.reply(embed=embed,view = view)

class DuplicateTask(discord.ui.View):
    def __init__(self,og_msg,title,message_content,attachments):
        super().__init__()
        self.title = title
        self.message_content = message_content
        self.attachments = attachments
        self.og_msg = og_msg
    
    @discord.ui.button(label="Yes",style=ButtonStyle.green)
    async def yes(self,button:discord.ui.Button,interaction:discord.Interaction):
        await interaction.response.defer()
        button.disabled = True
        description = ""
        if (self.message_content != ""):
            description = getTaskDescription(self.message_content)
        attachement_links = [attachement.url for attachement in self.attachments]
        if (len(attachement_links) > 0):
            description = description + "\n\nAttachments:\n" + "\n".join(attachement_links)
        task = createTask(self.title, description)
        if task == None:
            await interaction.response.send_message("Error creating task")
            return
        view = ClickupTask(task)
        embed = discord.Embed(title=task.name, description=task.description, color=0x00ff00)
        embed.add_field(name="Status", value=task.status.status, inline=True)
        embed.add_field(name="Priority", value="None", inline=True)  # hack
        view.add_item(discord.ui.Button(label="Open in Clickup", style=ButtonStyle.link, url=task.url))
        #send message in the channel
        await interaction.message.delete()
        ctx = await bot.get_context(self.og_msg)
        await ctx.reply(embed=embed,view = view)

    @discord.ui.button(label="No",style=ButtonStyle.red)
    async def no(self,button:discord.ui.Button,interaction:discord.Interaction):
        await interaction.message.edit(view=None)
        await interaction.response.defer()


class ClickupTask(discord.ui.view.View):
    def __init__(self,task):
        super().__init__()
        self.task = task

    # @discord.ui.select(
    #     placeholder="Change Status",
    #     options=[discord.SelectOption(
    #         label=status.status, value=status.status) for status in statuses_list]
    # ) 

    # async def change_status(self,select:discord.ui.Select,interaction:discord.Interaction):
    #     self.task.status = select.values[0]
    #     self.task.update(status = select.values[0])
    #     await self.updateTaskDetails(interaction)
    #     #update embed
    
    # async def updateTaskDetails(self, interaction: discord.Interaction):
    #     embed = discord.Embed(title=self.task.name,
    #                           description=self.task.description, color=0x00ff00)
    #     embed.add_field(name="Status", value=self.task.status, inline=True)
    #     priority = self.task.priority
    #     if(priority != None):
    #         priority = Priority(int(priority)).name
    #     else:
    #         priority = "None"
    #     embed.add_field(name="Priority", value= priority, inline=True)
    #     await interaction.response.edit_message(embed=embed)
        

    # @discord.ui.select(
    #     placeholder="Set Priority",
    #     options=[discord.SelectOption(
    #         label=Priority(priority).name, value= str(priority)) for priority in range(1,5)]
    # )

    # async def set_priority(self,select:discord.ui.Select,interaction:discord.Interaction):
    #     self.task.priority = select.values[0]
    #     self.task.update(priority = int(select.values[0]))
    #     await self.updateTaskDetails(interaction)

# command error
@bot.event
async def on_command_error(ctx, error):
    return # will remove if we add commands later
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing required argument")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command")
    else:
        await ctx.send("An error occured")
        raise error
    


bot.run(token)