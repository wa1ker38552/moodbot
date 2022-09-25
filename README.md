# moodbot
```pip install moodbot```

MoodBot is a mood adaptive chatbot that calculates moods from an input statement and generates an response. MoodBot was created as a project for Los Altos Hacks VI.

MoodBot works by finding sentence similarities using Cosine Similarity. The sentenced are tokenized using NLTK to plug into the cosine formula. We then compared already trained input and output statements agianst each other to find matches that are within a specified threshold.

MoodBot when imported, has no pre-trained data. To train MoodBot, you can use it's training functions to train data from .json files. MoodBot finds conversations within the raw message files by finding time proximity between messages and checking for repeat message authors. After a conversation with one input statement and one output statement is created, MoodBot can find the best matching input statement to an output statement using self.response.

Basic Example:

```py
from moodbot import discord_trainer
from moodbot import chatbot

trainer = discord_data(token)
raw_data = trainer.query_channel(CHANNEL_ID, limit=10000)
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

client = chatbot()
client.train('data/CHANNEL_ID')

print(client.response('Hello!').content)
```
