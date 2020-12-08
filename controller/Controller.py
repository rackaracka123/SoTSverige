import discord
from model import ChannelManager

class Controller():
    def __init__(self, client):
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
            except:
                print("Wrong in channel (after)")
        if before is not None:
            try:
                await self.controller.tryDeleteChannel(before.channel)
            except:
                print("Wrong in channel (before)")
        try:
            await self.controller.sortChannels(before.channel.category)
        except:
            await self.controller.sortChannels(after.channel.category)