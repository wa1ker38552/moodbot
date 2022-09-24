import os
from moodbot import chatbot
from moodbot import discord_trainer


# train data from Discord
token = 'TOKEN'

# train messages from specified channel
raw_data = discord_data(token).query_channel(CHANNEL_ID, limit=10000)
data = []
for message in raw_data:
    data.append({
        'content': message.content,
        'author': message.author_id,
        'timestamp': message.timestamp,
    })

# load into json
with open(f'data/CHANNEL_ID.json', 'w') as file:
    file.write(json.dumps(data, indent=4))

# initialize chatbot
client = chatbot()

# train the chatbot
client.train('data/CHANNEL_ID.json', remove=['@', 'https://', ''], threshold=60)

while True:
  response = client.response(input('>> '), mode='random', search_range=10)
  print(response.content)
