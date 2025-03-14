import openai
import numpy as np
import json

openai.api_key = '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'

class Similarity():
    def __init__(self):
        self.embedding_list = []
        speed = 0
    def calculate_embedding(self, text):
        resp = openai.Embedding.create(
            input = [text],
            engine = "text-embedding-3-small")
        resp = resp['data'][0]['embedding']
        return resp
    def findText(self, prompt, eval):
        max = 0.4
        success = ""
        with open('textExplanation/text.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Access the list of videos
        texts = data['text']
        prompt_embedding = self.calculate_embedding(prompt)
        # Iterate through the videos and print their details
        for i, text in enumerate(texts):
            sval = np.dot(eval[i], prompt_embedding)
            if sval > max:
                success = text['description']
                max = sval
        return success

    def create_embedding_list(self):
        with open('textExplanation/text.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

            # Access the list of videos
        texts = data['text']

        # Iterate through the videos and print their details
        for text in texts:
            self.embedding_list.append(self.calculate_embedding(text['topic']))
        return self.embedding_list