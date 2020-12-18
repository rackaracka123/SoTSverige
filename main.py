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
async def on_raw_reaction_add(reaction):
    await controller.onReactAdd(reaction)

@client.event
async def on_raw_reaction_remove(reaction):
    await controller.onReactRemove(reaction)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await controller.onCheckMessage(message, "/")
client.run(open("discord_auth.txt").read())