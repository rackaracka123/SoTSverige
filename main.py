import discord
import controller.Controller

client = discord.Client()
controller = controller.Controller.Controller(client)
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_voice_state_update(member, before, after):
    print("Voice state is not enabled")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
client.run(open("discord_auth.txt").read())