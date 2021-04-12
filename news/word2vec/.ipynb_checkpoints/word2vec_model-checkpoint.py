import gensim

class Word2VecModel():
    def __init__(self, path='./news/word2vec/baomoi.model.bin'):
        self.model = gensim.models.KeyedVectors.load_word2vec_format(path, binary=True)

    def n_similarity(self, vec1, vec2):
        vec1 = list(filter(lambda x: x in self.model.vocab.keys(), vec1))
        vec2 = list(filter(lambda x: x in self.model.vocab.keys(), vec2))
        try:
            return self.model.n_similarity(vec1, vec2)
        except ZeroDivisionError:
            return 0.0