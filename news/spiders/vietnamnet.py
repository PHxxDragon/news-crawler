import scrapy
import functools
from news.items import *
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Compose, Join, MapCompose
from w3lib.html import remove_tags
from scrapy.utils.request import request_fingerprint
import logging
from datetime import datetime
from news.utils import normalize_vn_string
from news.tokenizer.stopwords_remover import StopwordsRemover
from news.word2vec.word2vec_model import Word2VecModel
from news.tokenizer.dict_models import LongMatchingTokenizer
import timeit

class VietnamnetSpider(scrapy.Spider):
    name = 'vietnamnet'

    allowed_domains = ['vietnamnet.vn']

    start_urls = ['https://vietnamnet.vn/']

    logger = logging.getLogger('vietnamnetSpiderLogger')
    fileHander = logging.FileHandler("./log/vietnamnetSpider" + str(datetime.now()) + ".log")
    logger.addHandler(fileHander)

    query = [u"bóng đá"]

    lm_tokenizer = LongMatchingTokenizer()
    sm_remover = StopwordsRemover()
    word2vec = Word2VecModel()

    count = 0

    def __init__(self):
        self.query = list(functools.reduce(lambda x, y: x + y, map(lambda x: self.lm_tokenizer.tokenize(x), self.query), []))
        self.logger.info("Query tokens : " + str(self.query))

    def parse(self, response: scrapy.http.Response, **kwargs):
        self.logger.info('Called method \"parse\" for url : ' + response.url)
        ancestor_score = 0.25 * (kwargs['score'] if 'score' in kwargs.keys() else 0)
        self.logger.info('This link has score : ' + str(ancestor_score))
        if 'context' in kwargs:
            self.logger.info('This link has context score : ' + str(kwargs['context']))
        if 'ancestor' in kwargs:
            self.logger.info('This link has ancestor score : ' + str(kwargs['ancestor']))
        self.logger.info('Count : ' + str(self.count))
        self.count += 1

        if len(response.css(".ArticleDetail")) != 0:
            self.logger.info("ArticleDetail detected, creating item...")
            news_loader = ItemLoader(item=NewsItem(), response=response)
            news_loader.default_input_processor = MapCompose(remove_tags)
            news_loader.default_output_processor = TakeFirst()
            news_loader.add_value("url", response.url)
            news_loader.add_css("title", ".ArticleDetail h1")
            news_loader.add_css("dateAndTime", ".ArticleDate", MapCompose(lambda x: ' '.join(x.split())))
            news_loader.add_css("bodyText", "#ArticleContent p", Join(' '))
            news_loader.add_css("tags", ".tagBoxContent ul li a", Join(' '))

            self.logger.info("calculating content score :")
            content = response.xpath("//div/p/descendant-or-self::*/text()").getall()
            normalized_string = normalize_vn_string(' '.join(content))
            tokens = self.lm_tokenizer.tokenize(normalized_string)
            vec = list(self.sm_remover.removeStopwords(tokens))

            content_score = 100 * self.word2vec.n_similarity(vec, self.query)
            self.logger.info("content score : " + str(content_score))
            ancestor_score += content_score

            yield news_loader.load_item()

        if self.count > 700:
            return

        if 'roots' in kwargs.keys(): self.logger.info("This link is called from : " + str(kwargs['roots']))
        else: kwargs['roots'] = []

        newRoots = kwargs['roots'] + [response.url]
        params = {'roots': newRoots}

        links = response.xpath("//a[@href]")

        for link in links:
            url = response.urljoin(link.xpath("./@href").get())
            if not url.startswith('https'):
                continue

            urlContext = link.xpath("./ancestor::*[name() = 'div' or name() = 'li'][1]/descendant-or-self::*/text()").getall()

            normalized_string = normalize_vn_string(' '.join(urlContext))
            tokens = self.lm_tokenizer.tokenize(normalized_string)
            vec = list(self.sm_remover.removeStopwords(tokens))
            
            context_score = 100 * self.word2vec.n_similarity(vec, self.query) 
            
            score = int(context_score + ancestor_score)

            params['score'] = score
            params['context'] = context_score
            params['ancestor'] = ancestor_score
            
            yield scrapy.Request(url, callback=self.parse, priority=score, cb_kwargs=params)

    