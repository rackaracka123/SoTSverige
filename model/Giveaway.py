import discord

class Giveaway():
    def __init__(self, client):
        self.client = client
    async def handleReact(self, reaction : discord.RawReactionActionEvent, message : discord.Message):
        if message.content.startswith("**"): #**LOOT-HAUL GIVEAWAY
            member = discord.utils.get(self.client.get_all_members(), id=reaction.user_id)
            if len([x for x in member.roles if x.name == "Pirate Legend"]) == 1:
                return
            await message.channel.send("Tack <@" + str(reaction.user_id) + "> för din anmälan. Skicka en bild på dina titles till <@168789811816169472> för att säkerställa att du är inte Pirate Legend")
        if message.content.startswith("Tack "):
            await message.edit(content="Du har blivigt accepterad: <@" + str(message.mentions[1].id) + ">")