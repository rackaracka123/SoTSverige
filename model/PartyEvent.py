import discord
from datetime import datetime
from datetime import timedelta
from babel.dates import format_datetime
import asyncio

class PartyEvent():
    def __init__(self, client : discord.client, maxPlayers):
        self.client = client
        self.maxPlayers = maxPlayers
        self.alertTask = False
    def initGuild(self, guild : discord.Guild):
        self.eventChannel = discord.utils.get(guild.channels, name="event-anmälan")
        self.infoChannel = discord.utils.get(guild.channels, name="event-info")
        self.templateChannel = discord.utils.get(guild.channels, name="party-pirate-template")
    def setMax(self, nrMax):
        self.maxPlayers = nrMax
    def setLeaders(self, leaders):
        self.leaders = leaders
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
    def getPlatserString(self):
        return str(self.maxPlayers - len(self.leaders)) + " (" + str(self.maxPlayers) + ") *(Totalt " + str(self.maxPlayers) + " varav " + str(len(self.leaders)) + " platser reserverade för Partypirat.)*"
    async def sendInfoMessage(self, saturday):
        saturday = format_datetime(saturday, format="EEEE d MMMM Y", locale='sv_SE')
        template = await self.getTemplate()
        leadersStr = ""
        for x in self.leaders:
            leadersStr +="<@" + str(x) + "> "
        return await self.infoChannel.send(template.content.format(tid=saturday, queue="<#" + str(self.eventChannel.id) + ">", leaders=leadersStr, platser=self.getPlatserString()))
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
        embed.add_field(name= str(len(embed.fields) + 1) + " " + member.name + "#" + member.discriminator , value="-"*2*len(member.name), inline=False)
      
        if len(embed.fields) >= self.maxPlayers - 1:
            embed.insert_field_at(self.maxPlayers, name="🚧 Event anmälan är nu full 🚧", value= "alla under denna rad är reserver", inline=False)

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

            if "Event" in name or name == user.name + "#" + user.discriminator:
                counter-=1
                continue
            else:
                embed.add_field(name = str(counter) + " " + name, inline=False, value=x.value)

        embed.title="Event kö (Antalet personer: " + str(len(embed.fields)) + "/" + str(self.maxPlayers) + ")"
        if len(embed.fields) >= self.maxPlayers:
            embed.insert_field_at(self.maxPlayers, name="'🚧 Event anmälan är nu full 🚧", value= "alla under denna rad är reserver", inline=False)
        
        embed.set_footer(text="Bot skapad av: @rackaracka#6651")
        await queueMsg.edit(embed=embed)

    async def alertQueue(self, guild : discord.Guild):
        self.initGuild(guild)
        msg = await self.getQueueMsg()
        counter = 0
        
        for x in msg.embeds[0].fields:
            if "#" in x.name:
                counter+=1
                name = x.name[len(str(counter)) + 1:]
                member = guild.get_member_named(name)
                await member.send("**Du är i kö till Sea of Thieves Sveriges event idag**\nhttps://discord.gg/dHVPqUKfJb Se till att infinna dig här på utsägen tid för att vara med.")

    def calculateMinutesToEvent(self):
        a = datetime.now()
        sat = self.getNextSaturday()
        sat = sat.replace(year=sat.date().year, month=sat.date().month, day=sat.date().day, hour=12, minute=27)
        return round((sat-a).total_seconds()/60)
    async def startAlertTimer(self, guild):
        if self.calculateMinutesToEvent() < 0:
            return
        await asyncio.sleep(self.calculateMinutesToEvent() * 60)
        await self.alertQueue(guild)
        self.alertTask = False
        
    async def createAlertTask(self, guild):
        if self.alertTask == False:
            self.alertTask = True
            loop = asyncio.get_event_loop()
            loop.create_task(self.startAlertTimer(guild))