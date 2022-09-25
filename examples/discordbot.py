import moodbot
import discord
import nltk
import os

client = discord.Bot()


@client.slash_command(description='Show debug data')
async def debug(ctx):
    embed = discord.Embed()
    embed.title = 'Debug'
    embed.color = 0x93C4FF
    embed.add_field(name='Latency', value=f'`{round(client.latency, 3)}` ms', inline=False)
    embed.add_field(name='Trained', value=f'`{len(chatbot_client.conversations)}`', inline=False)
    await ctx.send(embed=embed)


@client.slash_command(description='Get a response from the bot')
async def response(ctx, input):
    await ctx.defer(ephemeral=True)
    response = chatbot_client.response(input)
    await ctx.send(response.content)

@client.slash_command(description='Train the bot with some data')
async def train(ctx, input, output):
    chatbot_client.manual_train(input, output)
    await ctx.send(f'Succesfully trained conversation set `{input}`, `{output}`')

@client.slash_command(description='Help command')
async def help(ctx):
    embed = discord.Embed()
    embed.title = 'Help'
    embed.color = 0x93C4FF
    embed.description = '`/debug`: Show debug information\n`/response [text]`: Generate a response from the bot\n`/train [input] [output]`: Train the ai with statement'

    await ctx.send(embed=embed)

# download punkt from nltk
nltk.download('punkt')

# initialize and train
chatbot_client = moodbot.chatbot()
for file in os.listdir('data/'):
    chatbot_client.train(f'data/{file}', remove=['@', 'https://', ''])

client.run('TOKEN')
