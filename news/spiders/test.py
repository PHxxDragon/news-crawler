#!/usr/bin/python
# -*- coding: utf8 -*-
import scrapy
import logging
from news.tokenizer.dict_models import LongMatchingTokenizer
from w3lib.html import remove_tags
from news.utils import normalize_vn_string
from news.utils import cosine_similarity
from news.tokenizer.stopwords_remover import StopwordsRemover
from news.word2vec.word2vec_model import Word2VecModel
from collections import Counter


class TestSpider(scrapy.Spider):
    name = 'test'
    allowed_domains = ['vietnamnet.vn']
    start_urls = ['http://vietnamnet.vn/']

    logger = logging.getLogger('test')
    fileHandler = logging.FileHandler('test.log')
    logger.addHandler(fileHandler)
    lm_tokenizer = LongMatchingTokenizer()
    sw_remover = StopwordsRemover()
    query = [u"thể_thao", u"bóng_đá"]
    word2vec = Word2VecModel()

    def parse(self, response):
        links = response.xpath("//a[@href]")
        for link in links:
            url = response.urljoin(link.xpath("./@href").get())
            if not url.startswith('https'):
                continue
            self.logger.info(url)
            urlContext = link.xpath("./ancestor::*[name() = 'div' or name() = 'li'][1]/descendant-or-self::*/text()").getall()
            nvs = normalize_vn_string(' '.join(urlContext))
            tokens = self.lm_tokenizer.tokenize(nvs)
            vec = list(self.sw_remover.removeStopwords(tokens))
            self.logger.info(vec)
            self.logger.info(self.word2vec.n_similarity(vec, self.query))
        yield None