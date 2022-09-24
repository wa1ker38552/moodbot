from nltk.tokenize import word_tokenize
from datetime import datetime
from data_mine import message
import moodbot
import random
import time
import json

class chatbot:
    def __init__(self):
        # raw_memory contains raw message data
        # conversations includes parsed conversation data

        self.raw_memory = []
        self.conversations = []
        self.responses = []
        self.stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

    def train(self, file, remove=[], threshold=60):
        # file must be json in this format:
        # [
        #   {
        #       'content': ...,
        #       'author': ...,
        #       'timestamp': y-m-dTh-m-s
        #   }
        # ]
        with open(file, 'r') as file:
            self.raw_memory.extend(json.loads(file.read()))

        # convert to <data_mine.message objects>
        self.memory = [message(item, type='') for item in self.raw_memory]

        # find conversations within memory
        for i, item in enumerate(self.memory):
            try:
                if item.author_id == self.memory[i+1].author_id: pass
                elif len(set(remove).intersection(set(item.content.split()))) > 0: pass
                elif len(set(remove).intersection(set(self.memory[i+1].content.split()))) > 0: pass
                else:
                    # input date

                    id = item.timestamp.split('+')[0].split('T')[0]
                    it = item.timestamp.split('+')[0].split('T')[1]
                    input = datetime.strptime(f'{id} {it}', '%Y-%m-%d %H:%M:%S')

                    od = self.memory[i+1].timestamp.split('+')[0].split('T')[0]
                    ot = self.memory[i+1].timestamp.split('+')[0].split('T')[1]

                    output = datetime.strptime(f'{od} {ot}', '%Y-%m-%d %H:%M:%S')

                    if (input-output).total_seconds() < 60:
                        self.conversations.append({
                            'input': item.content,
                            'output': self.memory[i+1].content,
                            'delta': (input-output).total_seconds()
                        })
            except IndexError:
                # can't count last message
                pass

    def train_responses(self):
        # check if there are responses to train
        if len(self.responses) > 1:
            try:
                for i, response in enumerate(self.responses):
                    # train individual responses between output and human input
                    self.conversations.append({
                        'input': response['output'],
                        'output': self.responses[i+1]['input'],
                        'delta': None
                    })
            except IndexError:
                # indexed response out of range
                pass

    def calculate_cosine(self, data_point, decimal, count, input):
        # compare input statements within conversations dataset
        output = data_point['input']

        l1, l2 = [], []

        # tokenize words if they're not a stop word
        x_vector = {word for word in word_tokenize(input) if word not in self.stop_words}
        y_vector = {word for word in word_tokenize(output) if word not in self.stop_words}

        rvector = x_vector.union(y_vector)
        for w in rvector:
            if w in x_vector: l1.append(1)
            else:l1.append(0)

            if w in y_vector: l2.append(1)
            else:l2.append(0)

        c = 0
        # calculate cosine similarity
        for i in range(len(rvector)):
            c += (l1[i] * l2[i])

        # unable to find similarity
        try:
            cosine = c / float((sum(l1) * sum(l2)) ** 0.5)
        except ZeroDivisionError:
            cosine = 0.0

        self.similarity_data.append(round(cosine, decimal))
        if count == len(self.conversations)-1: self.unready[0] = False

    def response(self, input, search_range=10, mode='random', decimal=3):
        start = time.time()
        self.similarity_data = []
        self.unready = [True]

        for i, data_point in enumerate(self.conversations):
            self.calculate_cosine(data_point, decimal, i, input)

        while self.unready[0]: pass

        possible_points = []
        for i, point in enumerate(self.similarity_data):
            # find proximity within similarity data
            r1 = float(max(self.similarity_data))-(0.01*search_range)
            r2 = float(max(self.similarity_data))+(0.01*search_range)

            # generate float range between max value and thresholds
            # python doesn't allow for range(float, float)
            if point in [x/(10**decimal) for x in range(int(r1*(10**decimal)), int(r2*(10**decimal))+1)]:
                possible_points.append(i)

        if mode == 'random':
            # random input from range
            closest_input = self.conversations[random.choice(possible_points)]['input']
            closest_output = self.conversations[random.choice(possible_points)]['output']

            # generate raw range min-max
            raw = [x/(10**decimal) for x in range(int(r1*(10**decimal)), int(r2*(10**decimal))+1)]
            response = moodbot.output(closest_input, closest_output, [min(raw), max(self.similarity_data)], time.time() - start)

        elif mode == 'match':
            # exact closest input

            closest_input = self.conversations[self.similarity_data.index(max(self.similarity_data))]['input']
            closest_output = self.conversations[self.similarity_data.index(max(self.similarity_data))]['output']

            response = moodbot.output(closest_input, closest_output, max(self.similarity_data), time.time() - start)

        # train current conversation
        self.responses.append({
            'input': input,
            'output': response.content,
            'delta': time.time()-start
        })
        # train self responses
        self.train_responses()
        return response