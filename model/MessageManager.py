import discord
class MessageManager:
    def __init__(self, client : discord.Client):
        self.client = client
    async def getMessageById(self, messageId):
        for x in self.client.get_all_channels():
            if x.type.name == "category" or "voice" in x.type.name:
                continue
            for y in await x.history(limit=100).flatten():
                if y.id == messageId:
                    return y