# -*- coding: utf-8 -*-
# @Time    : 18-9-24 下午10:35
# @Author  : Arjun

from elasticsearch_dsl import Date,Completion, Keyword, Text,DocType,Integer
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=["127.0.0.1"])


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}

ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])

class Spider(DocType):

    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")
    update_time = Date()
    url = Keyword()
    platform = Text(analyzer="ik_max_word")
    news_time = Integer()

    class Meta:
        index = "news_spider"
        doc_type = "tp_news"

if __name__ == '__main__':
    Spider.init()