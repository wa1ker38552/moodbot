# moodbot
```pip install moodbot```

MoodBot is a mood adaptive chatbot that calculates moods from an input statement and generates an response. MoodBot was created as a project for Los Altos Hacks VI.

MoodBot works by finding sentence similarities using Cosine Similarity. The sentenced are tokenized using NLTK to plug into the cosine formula. We then compared already trained input and output statements agianst each other to find matches that are within a specified threshold. Since Cosine Similarity works by finding and tokenizing words in two statements, if MoodBot is comparing a short statement to a long statement, it will likely find many possible outputs with high confidence even if those outputs do not necessarily make sense.

MoodBot when imported, has no pre-trained data. To train MoodBot, you can use it's training functions to train data from .json files. MoodBot finds conversations within the raw message files by finding time proximity between messages and checking for repeat message authors. After a conversation with one input statement and one output statement is created, MoodBot can find the best matching input statement to an output statement using self.response.

MoodBot can currently train off Discord and Google Chat. To train either one, use `moodbot.discord_trainer` or `moodbot.gchat_trainer`. Some there is a possibilty that users don't have Google workspace, data from Google Chat has to be manually pasted into a text file which the trainer reads and parses into json. Examples of file format are in `/examples`. To get raw gchat data, simply highlight the chatroom up until the message you want and paste them into a txt file.

Basic Example (Discord):

```py
from moodbot import discord_trainer
from moodbot import chatbot
import json

trainer = discord_trainer(token)
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

Basic Example (gchat)
```py
import moodbot

client = moodbot.chatbot()

trainer = moodbot.googlechat_trainer('data.txt')
# upload data to data.json
trainer.format_data('data.json')

client.train('data.json', remove=[''])
```
