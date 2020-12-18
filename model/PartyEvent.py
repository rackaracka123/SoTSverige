import discord
from datetime import datetime
from datetime import timedelta
from babel.dates import format_datetime

class PartyEvent():
    def __init__(self, client : discord.client, maxPlayers):
        self.client = client
        self.maxPlayers = maxPlayers
    def initGuild(self, guild : discord.Guild):
        self.eventChannel = discord.utils.get(guild.channels, name="event-anmälan")
        self.infoChannel = discord.utils.get(guild.channels, name="event-info")
        self.templateChannel = discord.utils.get(guild.channels, name="party-pirate-template")
    def setMax(self, nrMax):
        self.maxPlayers = nrMax
    async def purgeEventChannel(self):
        await self.eventChannel.purge()
    def distance(self, x, y):
        if x >= y:
            result = x - y
        else:
            result = y - x
        return result
    def getNextSaturday(self):
        currentDate = datetime.now()
        currentDate = currentDate + timedelta(days = self.distance(currentDate.weekday(), 5))
        return currentDate
    async def sendInfoMessage(self, saturday):
        saturday = format_datetime(saturday, format="EEEE d MMMM Y", locale='sv_SE')
        template = await self.getTemplate()
        return await self.infoChannel.send(template.content.format(tid=saturday, queue="<#" + str(self.eventChannel.id) + ">"))
    async def reactToEventMessage(self):
        message = await self.getQueueMsg()
        try:
            await message.add_reaction(discord.utils.get(self.eventChannel.guild.emojis, name="yes"))
        except:
            await message.add_reaction("👌")
    async def createQueueMessage(self):
        embed=discord.Embed(title="Event kö")
        await self.eventChannel.send(embed=embed)
    async def getTemplate(self):
        arr = await self.templateChannel.history(limit=1).flatten()
        return arr[0]
    async def getQueueMsg(self):
        arr = await self.eventChannel.history(limit=1).flatten()
        return arr[0]
    async def joinQueue(self, member : discord.member):
        self.initGuild(member.guild)
        queueMsg = await self.getQueueMsg()
        embed = discord.Embed()
        
        for counter, x in enumerate(queueMsg.embeds[0].fields):
            name = x.name[len(str(counter)) + 1:]
            if "Event" in name:
                continue
            embed.add_field(name=x.name, inline=False, value=x.value)
        
        
        embed.title="Event kö (Antalet personer: " + str(len(embed.fields) + 1) + "/" + str(self.maxPlayers) + ")"
      
        if len(embed.fields) >= self.maxPlayers - 1:
            embed.add_field(name= str(len(queueMsg.embeds[0].fields)) + " " + member.name , value="-"*2*len(member.name), inline=False)
            embed.insert_field_at(self.maxPlayers, name="🚧 Event anmälan är nu full 🚧", value= "alla under denna rad är reserver", inline=False)
        else:
            embed.add_field(name= str(len(queueMsg.embeds[0].fields) + 1) + " " + member.name , value="-"*2*len(member.name), inline=False)

        embed.set_footer(text="Bot skapad av: @rackaracka#6651")
        await queueMsg.edit(embed=embed)

    async def leaveQueue(self, user : discord.member, guild : discord.guild):
        self.initGuild(guild)
        queueMsg = await self.getQueueMsg()
        embed = discord.Embed()
        counter = 0
        for x in queueMsg.embeds[0].fields:
            counter+=1
            name = x.name[len(str(counter)) + 1:]

            if "Event" in name or name == user.name:
                counter-=1
                continue
            else:
                embed.add_field(name = str(counter) + " " + name, inline=False, value=x.value)

        embed.title="Event kö (Antalet personer: " + str(len(embed.fields)) + "/" + str(self.maxPlayers) + ")"
        if len(embed.fields) >= self.maxPlayers:
            embed.insert_field_at(self.maxPlayers, name="'🚧 Event anmälan är nu full 🚧", value= "alla under denna rad är reserver", inline=False)
        
        embed.set_footer(text="Bot skapad av: @rackaracka#6651")
        await queueMsg.edit(embed=embed)