import enum

import discord
from discord import ButtonStyle

from Helpers import AIHelper, ClickupHelper


class DuplicateTask(discord.ui.View):
    def __init__(self, og_msg, title, message_content, attachments):
        super().__init__()
        self.title = title
        self.message_content = message_content
        self.attachments = attachments
        self.og_msg = og_msg

    @discord.ui.button(label="Yes", style=ButtonStyle.green)
    async def yes(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        button.disabled = True
        description = ""
        if (self.message_content != ""):
            description = AIHelper.getTaskDescription(self.message_content)
        attachement_links = [attachement.url for attachement in self.attachments]
        if (len(attachement_links) > 0):
            description = description + "\n\nAttachments:\n" + "\n".join(attachement_links)
        task = ClickupHelper.createTask(self.title, description)
        if task == None:
            await interaction.response.send_message("Error creating task")
            return
        view = ClickupTask(task)
        embed = discord.Embed(title=task.name, description=task.description, color=0x00ff00)
        embed.add_field(name="Status", value=task.status.status, inline=True)
        embed.add_field(name="Priority", value="None", inline=True)  # hack
        view.add_item(discord.ui.Button(label="Open in Clickup", style=ButtonStyle.link, url=task.url))
        # send message in the channel
        await interaction.message.delete()
        await interaction.response.send_message(embed=embed, view=view)

    @discord.ui.button(label="No", style=ButtonStyle.red)
    async def no(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.message.edit(view=None)
        await interaction.response.defer()


class ClickupTask(discord.ui.view.View):
    def __init__(self, task):
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

class Priority(enum.Enum):
    """task priority enum"""

    NONE = 0
    URGENT = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

