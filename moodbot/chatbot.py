from nltk.tokenize import word_tokenize
from datetime import datetime
from moodbot import message
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

    def manual_train(self, input, output):
        # only train conversations not raw memory
        self.conversations.append({
            'input': input,
            'output': output,
            'delta': 0.0
        })

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

    def calculate_cosine(self, output, decimal, input):
        # compare input statements within conversations dataset
        X_list = input
        Y_list = word_tokenize(output)

        # sw contains the list of stopwords
        l1 = []
        l2 = []

        # remove stop words from the string
        X_set = {w for w in X_list if not w in self.stop_words}
        Y_set = {w for w in Y_list if not w in self.stop_words}

        # form a set containing keywords of both strings
        rvector = X_set.union(Y_set)
        for w in rvector:
            if w in X_set:l1.append(1)  # create a vector
            else:l1.append(0)
            if w in Y_set:l2.append(1)
            else:l2.append(0)

        c = 0
        for i in range(len(rvector)):
            c += l1[i] * l2[i]
        try:
            cosine = c / float((sum(l1)*sum(l2))**0.5)
        except ZeroDivisionError:
            cosine = 0.0

        self.similarity_data.append(round(cosine, decimal))

    def response(self, input, search_range=10, mode='random', decimal=3):
        start = time.time()
        mood_corpus = moodbot.FindMood()

        # find mood for possible input
        possible_input = mood_corpus.genInitResponse(input, True, ifResponse=False)

        # declared here since this resets after every response
        self.similarity_data = []
        tokenized = word_tokenize(input)

        for data_point in self.conversations:
            self.calculate_cosine(data_point['input'], decimal, tokenized)

        possible_points = []
        maxed = max(self.similarity_data)

        # find proximity within similarity data
        r1 = float(maxed) - (0.01 * search_range)
        r2 = float(maxed) + (0.01 * search_range)

        # using a counter variable faster than enumerating self.similarity_data
        i = 0
        for point in self.similarity_data:
            # generate float range between max value and thresholds
            # python doesn't allow for range(float, float)
            if point in [x/(10**decimal) for x in range(int(r1*(10**decimal)), int(r2*(10**decimal))+1)]:
                possible_points.append(i)

            i += 1

        if mode == 'random':
            # random input from range
            # find moods within range

            while True:
                seed = random.choice(possible_points)
                possible_output = mood_corpus.genInitResponse(self.conversations[seed]['input'], True, ifResponse=False)
                if abs(possible_input[0] - possible_output[0]) >= 0 or abs(possible_input[1] - possible_output[1]) >= 0:
                    break

            closest_input = self.conversations[seed]['input']
            closest_output = self.conversations[seed]['output']

            # generate raw range min-max
            raw = [x/(10**decimal) for x in range(int(r1*(10**decimal)), int(r2*(10**decimal))+1)]
            response = moodbot.output(closest_input, closest_output, [min(raw), maxed], time.time() - start, possible_output)

        elif mode == 'match':
            # exact closest input
            # generate emotion
            possible_output = mood_corpus.genInitResponse(self.conversations[self.similarity_data.index(maxed)]['input'], True, ifResponse=False)

            closest_input = self.conversations[self.similarity_data.index(maxed)]['input']
            closest_output = self.conversations[self.similarity_data.index(maxed)]['output']

            response = moodbot.output(closest_input, closest_output, maxed, time.time() - start, possible_output)

        # train current conversation
        self.responses.append({
            'input': input,
            'output': response.content,
            'delta': time.time()-start
        })
        # train self responses
        self.train_responses()
        return response
