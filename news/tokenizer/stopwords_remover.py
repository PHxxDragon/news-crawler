from news.tokenizer.utils import load_stopwords

class StopwordsRemover():
    def __init__(self, stopword_path = './news/tokenizer/vietnamese-stopwords-dash.txt'):
        self.stopwords_set = load_stopwords(stopword_path)

    def removeStopwords(self, vec):
        return filter(lambda x: x not in self.stopwords_set, vec)