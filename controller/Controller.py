import discord
from model import PartyEvent
from model import MessageManager
from model import Giveaway

class Controller():
    def __init__(self, client : discord.client):
        self.client = client
        self.partyEvent = PartyEvent.PartyEvent(client, 2)
        self.messageManager = MessageManager.MessageManager(client)
        self.giveaway = Giveaway.Giveaway(client)
    async def onCheckMessage(self, message : discord.Message, syntax):
        if [x.name.lower()=="party pirates" or x.name.lower()=="moderatorer" or x.name.lower()=="grundare" or x.name.lower()=="ägare" or x.name.lower()=="admin" for x in message.author.roles]:
            try:
                if message.content.lower().startswith(syntax + "purge"):
                    await message.channel.purge(limit=100000)
            except:
                None
            try:
                if message.content.lower().startswith(syntax + "placera "):
                    await self.partyEvent.placeUser(discord.utils.get(self.client.get_all_members(), id=message.raw_mentions[0]), int(message.content.split(" ")[2]), message.guild)
            except:
                None
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
            except Exception as e:
                await message.channel.send(e)
            try:
                if message.content.lower().startswith("/ersätt") and len(message.content.split(" ")) > 2:
                    msgId = int(message.content.split(" ")[1])
                    targetMsg = await self.messageManager.getMessageById(msgId)
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
            try:
                if message.content.lower().startswith("/gruppera"):
                    raw = message.content.replace("/gruppera", "").replace("<", "").replace(">", "").replace("!","").replace(" ", "")
                    groups = raw.split(":")
                    groupsList = []
                    for x in groups:
                        x = x.split("@")
                        x.remove("")
                        groupsList.append(x)
                    await self.partyEvent.groupPeople(message.guild, groupsList)
            except Exception as ex:
                print(ex)
        else:
            return
    async def onReactAdd(self, reaction : discord.RawReactionActionEvent):
        channel = discord.utils.get(self.client.get_all_channels(), id=reaction.channel_id)
        message = discord.message

        for x in await channel.history(limit=100).flatten():
            if x.id == reaction.message_id:
                message = x
        if reaction.user_id != self.client.user.id and channel.name == "event-anmälan":
            await self.partyEvent.joinQueue(reaction.member)
        if reaction.user_id != self.client.user.id and channel.name == "giveaway":
            await self.giveaway.handleReact(reaction, message)
    async def onReactRemove(self, reaction : discord.RawReactionActionEvent):
        channel = discord.utils.get(self.client.get_all_channels(), id=reaction.channel_id)
        message = discord.message
        user = await self.client.fetch_user(reaction.user_id)

        for x in await channel.history(limit=100).flatten():
            if x.id == reaction.message_id:
                message = x
        if reaction.user_id != self.client.user.id and channel.name == "event-anmälan":
            await self.partyEvent.leaveQueue(user, message.guild)
    async def onGuildAvailable(self, guild):
        await self.partyEvent.createAlertTask(guild)
    async def onVoiceUpdate(self, member, before, after):
        try:
            if after.channel.name=="Event rum":
                await self.partyEvent.onJoinEventChannel(member)
        except:
            None
        try:
            if before.channel.name=="Event rum":
                await self.partyEvent.onLeaveEventChannel(member)
        except:
            None