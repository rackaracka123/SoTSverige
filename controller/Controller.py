import discord
from model import PartyEvent
from model import MessageManager

class Controller():
    def __init__(self, client : discord.client):
        self.client = client
        self.partyEvent = PartyEvent.PartyEvent(client, 2)
        self.messageManager = MessageManager.MessageManager(client)
    async def onCheckMessage(self, message, syntax):
        if [x.name.lower()=="party pirat" or x.name.lower()=="moderatorer" or x.name.lower()=="grundare" or x.name.lower()=="ägare" or x.name.lower()=="admin" for x in message.author.roles]:
            try:
                if message.content.lower().startswith(syntax + "event") and len(message.raw_mentions) != 0:
                
                    self.partyEvent.setMax(int(message.content.split(" ")[1]))
                    self.partyEvent.setLeaders(message.raw_mentions)

                    self.partyEvent.initGuild(message.guild)
                    await self.partyEvent.eventChannel.send("Purging...")
                    await self.partyEvent.purgeEventChannel()

                    await self.partyEvent.sendInfoMessage(self.partyEvent.getNextSaturday())

                    await self.partyEvent.createQueueMessage()

                    await self.partyEvent.reactToEventMessage()

                    await self.partyEvent.createAlertTask(message.guild)
                elif "/event" in message.content.lower():
                    await message.channel.send("**Fel argument i kommandot**\nSkriv så här `/event [totalt antal] [pinga alla ledare här]`\n**Exempel:**\n/event 12 <@241255969106034688>")
            except:
                await message.channel.send("**Fel argument i kommandot**\nSkriv så här `/event [totalt antal] [pinga alla ledare här]`\n**Exempel:**\n/event 12 <@241255969106034688>")
            try:
                if message.content.lower().startswith("/ersätt") and len(message.content.split(" ")) > 2:
                    targetMsg = await self.messageManager.getMessageById(int(message.content.split(" ")[1]))
                    spaceCntr = 0
                    msg=""
                    for z in message.content:
                        if spaceCntr < 2:
                            if z == ' ':
                                spaceCntr+=1
                        else:
                            msg+=z
                    await targetMsg.edit(content=msg)
                    embed = discord.Embed()
                    embed.add_field(name="**Meddelandet byttes ut :)**\n(raderar kommando meddelandet för att rensa upp lite)", value="[länk till meddelandet hittas här](" + targetMsg.jump_url + ")", inline=False)
                    await message.channel.send(embed=embed)
                    await message.delete()
            except:
                await message.channel.send("**Fel argument i kommandot**\nSkriv så här `/ersätt [message id] [nytt meddelande här]`")
    async def onReactAdd(self, reaction : discord.RawReactionActionEvent):
        channel = discord.utils.get(self.client.get_all_channels(), id=reaction.channel_id)
        message = discord.message

        for x in await channel.history(limit=2).flatten():
            if x.id == reaction.message_id:
                message = x
        if reaction.user_id != self.client.user.id and channel.name == "event-anmälan":
            await self.partyEvent.joinQueue(reaction.member)
    async def onReactRemove(self, reaction : discord.RawReactionActionEvent):
        channel = discord.utils.get(self.client.get_all_channels(), id=reaction.channel_id)
        message = discord.message
        user = await self.client.fetch_user(reaction.user_id)

        for x in await channel.history(limit=2).flatten():
            if x.id == reaction.message_id:
                message = x
        if reaction.user_id != self.client.user.id and channel.name == "event-anmälan":
            await self.partyEvent.leaveQueue(user, message.guild)
    async def onGuildAvailable(self, guild):
        await self.partyEvent.createAlertTask(guild)