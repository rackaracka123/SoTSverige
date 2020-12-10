import discord
from model import ChannelManager

class Controller():
    def __init__(self, client : discord.client):
        self.client = client
        self.controller = ChannelManager.ChannelManager(client)
    async def onCheckVoiceState(self, member, before : discord.VoiceState, after : discord.VoiceState):        
        try:
            if after.channel == before.channel:
                return
        except:
            print(member + " did not change channel")
        if after is not None:
            try:
                await self.controller.checkJoinChannel(member, after.channel)
                print("Member joined " + after.channel.name)
            except:
                print("Member moved to a channel i cant see")
        if before is not None:
            try:
                deleted = await self.controller.tryDeleteChannel(before.channel)
                if deleted:
                    print("Member left " + before.channel.name + " (" + str(len(before.channel.members)) + "/" + str(before.channel.user_limit) + ") -> deleting it.")
                else:
                    print("Member left " + before.channel.name + " (" + str(len(before.channel.members)) + "/" + str(before.channel.user_limit) + ") -> not deleting it.")
            except:
                print("Member came from a channel i cant see")
        try:
            await self.controller.sortChannels(before.channel.category)
        except:
            await self.controller.sortChannels(after.channel.category)