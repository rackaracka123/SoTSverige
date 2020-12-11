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
            print(member.name + " did not change channel")
        if after is not None:
            if after.channel is not None:
                ch = await self.client.fetch_channel(after.channel.id)
                try:
                    await self.controller.checkJoinChannel(member, ch)
                    print(member.name + " joined " + ch)
                except:
                    print(member.name + " moved to a channel i cant see")
        if before is not None:
            if before.channel is not None:
                ch = await self.client.fetch_channel(before.channel.id)
                try:
                    deleted = await self.controller.tryDeleteChannel(ch)
                    if deleted:
                        print(member.name + " left " + ch.name + " (" + str(len(ch.members)) + "/" + str(ch.user_limit) + ") -> deleting it.")
                    else:
                        print(member.name + " left " + ch.name + " (" + str(len(ch.members)) + "/" + str(ch.user_limit) + ") -> not deleting it.")
                except:
                    print(member.name + " came from a channel i cant see")
            try:
                await self.controller.sortChannels(before.channel.category)
            except:
                await self.controller.sortChannels(after.channel.category)