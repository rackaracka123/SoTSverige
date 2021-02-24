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
        self.commandCentral = discord.utils.get(guild.channels, name="kommando-central")
        self.LoggChannel = discord.utils.get(guild.channels, name="party-logg-central")
    def setMax(self, nrMax):
        self.maxPlayers = nrMax
    def setLeaders(self, leaders):
        self.leaders = leaders
    async def purgeEventChannel(self):
        await self.eventChannel.purge()
    def distance(self, x, y):
        for day in range(7):
            if (x + day) % 7 == y:
                return day
    def getNextSaturday(self):
        currentDate = datetime.now()
        currentDate = currentDate + timedelta(days = self.distance(currentDate.weekday(), 5)) #0 = måndag, 1 = tisdag...
        return currentDate
    def getPlatserString(self):
        return str(self.maxPlayers - len(self.leaders)) + " (" + str(self.maxPlayers) + ") *(Totalt " + str(self.maxPlayers) + " varav " + str(len(self.leaders)) + " platser reserverade för Partypirat.)*"
    async def sendInfoMessage(self, saturday):
        saturday = format_datetime(saturday, format="EEEE d MMMM Y", locale='sv_SE')
        template = await self.getTemplate()
        leadersStr = ""
        for x in self.leaders:
            leadersStr +="<@" + str(x) + "> "
        return await self.infoChannel.send(template.format(tid=saturday, queue="<#" + str(self.eventChannel.id) + ">", leaders=leadersStr, platser=self.getPlatserString()))
    async def reactToEventMessage(self):
        message = await self.getQueueMsg()
        try:
            await message.add_reaction(discord.utils.get(self.eventChannel.guild.emojis, name="Yes"))
        except:
            await message.add_reaction("👌")
    async def createQueueMessage(self):
        await self.eventChannel.send("Event kö **Reagera nedan för att vara med** (Antalet personer: 0/" + str(self.maxPlayers) + ")\n")
    async def getMax(self, queueMsg):
        max = int(queueMsg.content.split(")")[0].split("/")[1])
        return max
    async def getTemplate(self):
        arr = await self.templateChannel.history(limit=1).flatten()
        return arr[0].content.replace("`", "")
    async def getQueueMsg(self):
        arr = await self.eventChannel.history(limit=100).flatten()
        return arr[len(arr) - 1]
    def messageToArray(self, message):
        queue = []
        for person in message.content.split("\n"):
            if "<@!" in person:
                queue.append(person.split(" "))
        return queue
    async def placeUser(self, user : discord.Member, position, guild : discord.Guild):
        await self.leaveQueue(user, guild)
        await self.joinQueue(user, pos=position)
    async def joinQueue(self, member : discord.member, *, pos=None):
        self.initGuild(member.guild)
        queueMsg = await self.getQueueMsg()
        self.maxPlayers = await self.getMax(queueMsg)
        queueArr = self.messageToArray(queueMsg)
        msgToSend = "Event kö **Reagera nedan för att vara med** (Antalet personer: " + str(len(queueArr) + 1) + "/" + str(self.maxPlayers) + ")\n"
        
        for counter, x in enumerate(queueArr):
            if pos is None:
                msgToSend += str(counter + 1) + " " + x[1] + "\n"
            else:
                if pos == counter + 1:
                    msgToSend+= str(counter + 1) + " <@!" + str(member.id) + ">\n"
                    if counter == self.maxPlayers - 1:
                        msgToSend+="🚧 Event anmälan är nu full 🚧\nAlla under denna rad är reserver\n"
                    counter+=1
                    msgToSend += str(counter + 1) + " " + x[1] + "\n"
                else:
                    msgToSend += str(counter + 1) + " " + x[1] + "\n"
            if counter == self.maxPlayers - 1:
                msgToSend+="🚧 Event anmälan är nu full 🚧\nAlla under denna rad är reserver\n"
        if pos is None:
            msgToSend+= str(len(queueArr) + 1) + " <@!" + str(member.id) + ">\n"
        if len(queueArr) + 1 == self.maxPlayers:
            msgToSend+="🚧 Event anmälan är nu full 🚧\nAlla under denna rad är reserver\n"
        msgToSend+="Bot skapad av: <@240772724006453248>"
        await queueMsg.edit(content=msgToSend)
        asyncio.get_event_loop().create_task(self.loggRegUnreg(member, "reg"))

    async def leaveQueue(self, user : discord.member, guild : discord.guild):
        self.initGuild(guild)
        queueMsg = await self.getQueueMsg()
        self.maxPlayers = await self.getMax(queueMsg)
        queueArr = self.messageToArray(queueMsg)
        msgToSend = ""

        counter = 0
        for x in queueArr:
            counter+=1
            if "Alla under denna rad är reserver" in x:
                counter-=1
                continue
            id = int(x[1].replace("<@!", "").replace(">", ""))

            if "Event" in x or id == user.id:
                counter-=1
                continue
            else:
                msgToSend+=str(counter) + " <@!" + str(id) + "> \n"

            if counter == self.maxPlayers:
                msgToSend+="🚧 Event anmälan är nu full 🚧\nAlla under denna rad är reserver\n"
        
        msgToSend+="Bot skapad av: <@240772724006453248>"
        title = "Event kö **Reagera nedan för att vara med** (Antalet personer: " + str(counter) + "/" + str(self.maxPlayers) + ")\n"
        await queueMsg.edit(content=title + msgToSend)
        asyncio.get_event_loop().create_task(self.loggRegUnreg(user, "unreg"))

    async def loggRegUnreg(self, member, action):
        if action == "reg":
            embed = discord.Embed(title=":inbox_tray: Kö")
            embed.add_field(name=datetime.today().now().strftime("%Y-%m-%d, %H:%M:%S"), value="<@" + str(member.id) + ">")
            await self.LoggChannel.send(embed=embed)
        elif action == "unreg":
            embed = discord.Embed(title=":outbox_tray: Kö")
            embed.add_field(name=datetime.today().now().strftime("%Y-%m-%d, %H:%M:%S"), value="<@" + str(member.id) + ">")
            await self.LoggChannel.send(embed=embed)
            
    async def alertQueue(self, guild : discord.Guild):
        self.initGuild(guild)
        msg = await self.getQueueMsg()
        counter = 0

        content = """**Kontakar personer i kön...**
"""
        loggMsg = await self.LoggChannel.send(content)

        for x in self.messageToArray(msg):
            try:
                if "Alla under denna rad är reserver" not in x:
                    counter+=1
                    id = int(x[1].replace("<@!", "").replace(">", ""))

                    member = guild.get_member(id)
                    await member.send("**Du är i kö till Sea of Thieves Sveriges event idag**\nhttps://discord.gg/dHVPqUKfJb Se till att infinna dig här på utsägen tid för att vara med.")
                    print("Successfully wrote to user " + x[1])
                    content+=str(counter) + " <@" + str(member.id) + "> Status: **Lyckades**\n"
                    await loggMsg.edit(content=content)
                if "Alla under denna rad är reserver" in x:
                    return
            except:
                content+=x[1] + " Status: **Misslyckades**\n"
                await loggMsg.edit(content=content)
                print("Error in writing to user " + x[1])
        content+="**Hoppas det går bra med eventet**"
        await loggMsg.edit(content=content)
    def calculateMinutesToEvent(self):
        a = datetime.now()
        sat = self.getNextSaturday()
        sat = sat.replace(year=sat.date().year, month=sat.date().month, day=sat.date().day, hour=18, minute=0)
        return round((sat-a).total_seconds()/60)
    async def onJoinEventChannel(self, member):
        embed = discord.Embed(title=":inbox_tray: Event rum")
        embed.add_field(name=datetime.today().now().strftime("%Y-%m-%d, %H:%M:%S"), value="<@" + str(member.id) + ">")
        self.initGuild(member.guild)
        await self.LoggChannel.send(embed=embed)
    async def onLeaveEventChannel(self, member):
        embed = discord.Embed(title=":outbox_tray: Event rum")
        embed.add_field(name=datetime.today().now().strftime("%Y-%m-%d, %H:%M:%S"), value="<@" + str(member.id) + ">")
        self.initGuild(member.guild)
        await self.LoggChannel.send(embed=embed)
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