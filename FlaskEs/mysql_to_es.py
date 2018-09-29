# -*- coding: utf-8 -*-
# @Time    : 18-9-25 下午2:47
# @Author  : Arjun

import pymysql
from models.elasearch import Spider
from elasticsearch_dsl.connections import connections
from newssearch import redis_store

es = connections.create_connection(Spider._doc_type.using)



def gen_suggest(index,info_tuple):
    """根据字符串生成搜索建议数组"""
    used_words = set()
    suggests = []
    for text,weight in info_tuple:
        if text:
            """调用es的_analyze方法进行分析字符串"""
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter': ["lowercase"]}, body=text)
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            new_words = anylyzed_words - used_words
        else:
            new_words = set()
        if new_words:
            suggests.append({"input":list(new_words),"weight":weight})
        return suggests


class MysqlMesToElastic(object):

    def __init__(self):
        pass

    # 获取数据库数据
    def get_mysql_data(self):
        id = 1
        db_zuker = pymysql.connect("", "", "", "", charset="utf8")
        cursor = db_zuker.cursor()
        # 取出最后一条数据
        # SQL_get_mes = "select * from tp_news order by id desc limit 1;"
        # cursor.execute(SQL_get_mes)
        # last_id = cursor.fetchone()['id']
        # print(last_id)
        while id <= 1500:
            dict_mes = {}
            SQL_get_mes = "select * from tp_news WHERE id = %s;" % (id)
            cursor.execute(SQL_get_mes)
            results = cursor.fetchone()
            print(results)
            # 如果有元素则分析元素
            if results:
                dict_mes = {
                    "id":results[0],
                    'title': results[1],
                    'content': results[2],
                    'update_time': results[3],
                    'url': results[4],
                    'platform': results[5],
                    'news_time': results[8],
                }
            id += 1
            if dict_mes:
                # 调用 process_item方法 向数据库中插数据
                try:
                    self.process_item(dict_mes)
                except Exception as e:
                    print(e)


    # 将数据写入到ES中
    def process_item(self,item):
        zuker = Spider()
        zuker.title = item['title']
        zuker.content = item['content']
        zuker.update_time = item['update_time']
        zuker.url = item['url']
        zuker.platform = item['platform']
        zuker.news_time = item['news_time']
        zuker.meta.id = item["id"]
        zuker.suggest = gen_suggest(Spider._doc_type.index,((zuker.title,10),(zuker.platform,5)))
        try:
            zuker.save()
        except Exception as e:
            print(e)
        redis_store.incr("news_counts")

if __name__ == "__main__":
    item = MysqlMesToElastic()
    item.get_mysql_data()
