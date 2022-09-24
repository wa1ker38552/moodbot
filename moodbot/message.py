class message:
    def __init__(self, obj, type='fromdiscord'):
        # create message object with attributes
        self.content = obj['content']

        # discord fetches author id from ['author']['id']
        if type == 'fromdiscord':
            self.author_id = obj['author']['id']
            self.id = obj['id']
        else:
            self.author_id = obj['author']

        self.timestamp = obj['timestamp'].split('.')[0]