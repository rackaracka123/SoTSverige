import discord

boatTypes = {2 : "Sloop", 3 : "Brig", 4 : "Galleon"}

class ChannelManager():
    def __init__(self, client : discord.client):
        self.client = client
    async def joinOrCreateVoiceChannelInCategory(self, member : discord.member, category : discord.CategoryChannel):
        pirate = category.guild.get_role(556416229099962368)
        if pirate is None:
            pirate = category.guild.get_role(785605832133050380)
        if category.name.lower().endswith("spelare"):
            if category.name[0].lower() == "X":
                return
            boatSize = int(category.name[0])
            channel = await category.create_voice_channel(boatTypes[boatSize] +  " - " + str(len(category.channels)), user_limit=boatSize)
            await member.move_to(channel)
    async def checkJoinChannel(self, member : discord.member, channel : discord.VoiceChannel):
        if channel is None:
            return
        if channel.name.lower().startswith("skapa"):
            await self.joinOrCreateVoiceChannelInCategory(member, channel.category)

    ##LEAVE VOICE CHANNEL -> DELETE
    
    def isChannelDeletable(self, channel : discord.VoiceChannel):
        return (channel.name.startswith(boatTypes[2]) or channel.name.startswith(boatTypes[3]) or channel.name.startswith(boatTypes[4])) and len(channel.members) == 0
    async def tryDeleteChannel(self, channel : discord.VoiceChannel):
        channel = await self.client.fetch_channel(channel.id)
        if self.isChannelDeletable(channel):
            await channel.delete()
    async def sortChannels(self, category : discord.CategoryChannel):
        if "spelare" in category.name.lower():
            counter = 1
            for x in category.channels:
                if x.name.lower().startswith("skapa"):
                    continue
                if str(counter) in x.name:
                    counter+=1
                else:
                    boatSize = int(category.name[0])
                    await x.edit(name=boatTypes[boatSize] + " - " + str(counter))
                    counter+=1