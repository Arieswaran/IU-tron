import Levenshtein
import discord

APP_FOLLOW_REVIEW_CHANNEL = 1116309975392849950
FILTERED_REVIEW_CHANNEL = 1070598072104656906


async def check_and_post_reviews(message: discord.Message, bot: discord.Client):
    if message.channel.id == APP_FOLLOW_REVIEW_CHANNEL:  # original channel where all app follow reviews are posted
        embed = message.embeds[0]
        msg = embed.description
        msg = msg.split("Hitwicket Cricket Games")[1].strip()
        rating, description, *other = msg.split("\n")
        if len(other) > 0:
            for i in range(len(other)):
                description = description + "\n" + other[i]
        by = embed.fields[0].value
        if (len(description.split(" ")) > 4 or len(
                description) > 20):  # filter out reviews with less than 4 words in description or less than 20 characters
            channel = bot.get_channel(FILTERED_REVIEW_CHANNEL)  # channel where we want to post the filtered reviews
            embed = discord.Embed(
                description=rating + "\n" + description + "\n" + by)
            await channel.send(embed=embed)


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
