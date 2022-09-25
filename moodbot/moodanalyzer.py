from nltk.tokenize import word_tokenize
import random
import json
import math


class FindMood:
    # emotion tuples will be in form of [happiness-sadness, angry/suprised-fear, #]

    def __init__(self):
        # Data in the form of sentence:mood triplet
        self.moodDictInit = json.loads(open('moodbot/training/initial.json', 'r').read())
        self.moodDictResponse = json.loads(open('moodbot/training/response.json', 'r').read())  # Data in the form of sentence:mood triplet
        self.moodDictCorr = json.loads(open('moodbot/training/relation.json', 'r').read())
        self.stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've",
                           "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
                           'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them',
                           'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll",
                           'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
                           'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or',
                           'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
                           'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from',
                           'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
                           'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
                           'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
                           'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now',
                           'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn',
                           "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn',
                           "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan',
                           "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't",
                           'wouldn', "wouldn't"]

    def calculate_cosine(self, a, b):
        # compare input statements within conversations dataset

        l1, l2 = [], []

        # tokenize words if they're not a stop word
        x_vector = {word for word in word_tokenize(a) if word not in self.stop_words}
        y_vector = {word for word in b if word not in self.stop_words}

        rvector = x_vector.union(y_vector)
        for w in rvector:
            if w in x_vector:
                l1.append(1)
            else:
                l1.append(0)

            if w in y_vector:
                l2.append(1)
            else:
                l2.append(0)

        c = 0
        # calculate cosine similarity
        for i in range(len(rvector)):
            c += (l1[i] * l2[i])

        # unable to find similarity
        try:
            cosine = c / float((sum(l1) * sum(l2)) ** 0.5)
        except ZeroDivisionError:
            cosine = 0.0

        return cosine

    def trainToDict(self, initial, response):
        useList = []
        similarList = []  # list of tuples - (sentence, similarity)
        sentenceList = []

        tokenized = word_tokenize(response)
        # once we have mood, we define another dict for responses - what sentence types are responded with what other sentence types
        for sentence1 in list(self.moodDictResponse.keys()):
            if self.calculate_cosine(sentence1, tokenized) > 0:
                similarList.append(((self.moodDictResponse[sentence1][0], self.moodDictResponse[sentence1][1]),
                                    self.calculate_cosine(sentence1, tokenized)))
                sentenceList.append(sentence1)
            # find sentence similarity with response and sentence1
            # append if above similarity to similarList

        avgResponse = [0, 0, 0]  # get avg between points in similarList
        for item in similarList:
            avgResponse[0] += item[0][0] * item[1]
            avgResponse[1] += item[0][1] * item[1]
            avgResponse[2] += item[1]  # cosine similarity

        if len(similarList) == 0:
            return None
        avgResponse[0] /= avgResponse[2]
        avgResponse[1] /= avgResponse[2]
        avgResponse[2] = 1

        # redefine plots of sets with similarity using avg of wholeb

        for sentences1 in sentenceList:
            useList = self.moodDictResponse[sentences1]
            self.moodDictResponse[sentences1] = [(useList[0] * useList[2] + avgResponse[0]) / (useList[2] + 1),
                                                 (useList[1] * useList[2] + avgResponse[1]) / (useList[2] + 1),
                                                 useList[2] + 1]

        # reset few things
        useList.clear()
        similarList.clear()
        sentenceList.clear()

        tokenized2 = word_tokenize(initial)
        # go through dictionary & compare with mooddict sentence similarity - only take the ones with certain amount of words or more in common
        for sentence in list(self.moodDictInit.keys()):
            if self.calculate_cosine(sentence, tokenized2) > 0:
                similarList.append(((self.moodDictInit[sentence][0], self.moodDictInit[sentence][1]),
                                    self.calculate_cosine(sentence, tokenized2)))
                sentenceList.append(sentence)
                # get response for sentence originally saved in dictionary & find avg between response and saved response & find closest response(tuple-wise)
            # find sentence similarity with initial and sentence
            # append if above certain similarity to similarList

        avgInit = [0, 0, 0]
        # get avg between points in similarList
        for item in similarList:
            avgInit[0] += item[0][0] * item[1]
            avgInit[1] += item[0][1] * item[1]
            avgInit[2] += item[1]

        if len(similarList) == 0:
            return None
        avgInit[0] /= avgInit[2]
        avgInit[1] /= avgInit[2]
        avgInit[2] = 1

        # also redifine plots of sets with similarity using avg of whole
        for sentences in sentenceList:
            useList = self.moodDictInit[sentences]
            self.moodDictInit[sentences] = [(useList[0] * useList[2] + avgInit[0]) / (useList[2] + 1),
                                            (useList[1] * useList[2] + avgInit[1]) / (useList[2] + 1), useList[2] + 1]

        # make relative correlation between mood initial and response & append into moodDictCorr
        self.moodDictResponse[response] = avgResponse
        self.moodDictInit[initial] = avgInit
        self.moodDictCorr[initial] = response

    def genNeutral(self):
        fin = "Dw I'll help you"
        org = (0.5, 0.5)
        for sentence in list(self.moodDictResponse.keys()):
            if math.dist(org, (self.moodDictResponse[sentence][0], self.moodDictResponse[sentence][1])) < math.dist(org,(self.moodDictResponse[fin][0],self.moodDictResponse[fin][1])):
                if random.randint(1, 100) < 50:
                    fin = sentence
        return fin

    def genInitResponse(self, initial, chooseemotion, ifResponse=True):
        # when receiving sentence with chatterbot, analyze mood first, then check moodDictCorr to find right mood, then find from self.moodDictResponse with +-0.1 mood that has most sentence similarity(to make it so that they are talking about same/similar things)
        tokenized = word_tokenize(initial)
        similarList = []
        for sentence in list(self.moodDictInit.keys()):
            if self.calculate_cosine(sentence, tokenized) > 0:
                similarList.append(((self.moodDictInit[sentence][0], self.moodDictInit[sentence][1]),
                                    self.calculate_cosine(sentence, tokenized)))

        avgInit = [0, 0, 0]
        # get avg between points in similarList
        for item in similarList:
            avgInit[0] += item[0][0] * item[1]
            avgInit[1] += item[0][1] * item[1]
            avgInit[2] += item[1]

        if len(similarList) == 0:
            if chooseemotion:
                return self.moodDictResponse[self.genNeutral()]
            else:
                return self.genNeutral()
        avgInit[0] /= avgInit[2]
        avgInit[1] /= avgInit[2]
        avgInit[2] = 1

        nearestInitResponse = "Dw I'll help you"

        for s2 in list(self.moodDictInit.keys()):
            if math.dist((avgInit[0], avgInit[1]), (self.moodDictInit[s2][0], self.moodDictInit[s2][1])) < math.dist(
                    (avgInit[0], avgInit[1]),
                    (self.moodDictInit[nearestInitResponse][0], self.moodDictInit[nearestInitResponse][1])):
                nearestInitResponse = s2

        if not ifResponse:
            if chooseemotion:
                return avgInit
            else:
                return nearestInitResponse

        nearestResponse = self.moodDictResponse[self.moodDictCorr[nearestInitResponse]]
        still = [-10, -10]
        fin = self.genNeutral()
        tokenized2 = word_tokenize(self.moodDictCorr[nearestInitResponse])
        for s3 in list(self.moodDictResponse.keys()):
            if self.calculate_cosine(s3, tokenized2) > 0:
                if math.dist((nearestResponse[0], nearestResponse[1]),
                             (self.moodDictResponse[s3][0], self.moodDictResponse[s3][1])) < math.dist(
                        (nearestResponse[0], nearestResponse[1]), (still[0], still[1])):
                    still = [self.moodDictResponse[s3][0], self.moodDictResponse[s3][1]]
                    fin = s3

        if chooseemotion:
            return self.moodDictResponse[fin]
        return fin
