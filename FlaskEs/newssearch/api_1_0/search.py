# -*- coding: utf-8 -*-
# @Time    : 18-9-28 下午3:25
# @Author  : Arjun

from . import api
from flask_restful import Resource
from newssearch.models import Spider
from flask import current_app,jsonify,request
from elasticsearch import Elasticsearch
from datetime import datetime
from newssearch import redis_store

client = Elasticsearch(hosts=["127.0.0.1"])


# @api.route("/")
# def index():
#     return "elk,elk,elk"

"""搜索提示功能"""
@api.route("/suggest")
def get_response():
    """获取用户要搜索的参数"""
    key_words = request.args.get("s","")
    re_datas = []
    if key_words:
        s = Spider.search()
        s = s.suggest("my_suggest",key_words,completion={
            "field": "suggest",
            "fuzzy": {
                "fuzziness": 1
            },
            "size":8
        })
        suggestions = s.execute_suggest()
        for macth in suggestions.my_suggest[0].options:
            source = macth._source
            re_datas.append(source["title"])
    return jsonify(data={"re_datas":re_datas})


"""搜索后"""
@api.route("/search")
def get_content():
    key_words = request.args.get("q","")

    """对每次搜索关键字在redis有序集合中分数加上增量"""
    redis_store.zincrby("keywords_set", key_words)

    """按分数排序,逆序排列所有成员"""
    top_search = redis_store.zrevrangebyscore("keywords_set","+inf", "-inf",start=0,num=5)

    """TypeError: b"" is not JSON serializable buge 解决方法"""
    top_search = [t.decode("utf-8") for t in top_search]

    page = request.args.get("p","1")
    try:
        page = int(page)
    except:
        page = 1

    start_time = datetime.now()
    response = client.search(
        index="news_spider",
        body={
            "query":{
            "multi_match": {
                "query": key_words,
                "fields": ["content","title","platform"]
                }
            },
            "from": (page-1)*10,
            "size": 10,
            "highlight": {
                "pre_tags": ["<span class='keyword'>"],  #搜索关键字高亮处理
                "post_tags": ["</span>"],
                "fields": {
                    "content": {},
                    "title": {},
                            }
                        }
            }
    )
    """获取总入库数量"""
    news_counts = int(redis_store.get("news_counts"))
    end_time = datetime.now()
    """获取查询时间"""
    last_seconds = (end_time-start_time).total_seconds()
    """获取查询的总条数"""
    total_nums = response["hits"]["total"]
    if (page % 10) >0:
        page_nums = int(total_nums/10) + 1
    else:
        page_nums = int(total_nums/10)

    hit_list = []
    for hit in response["hits"]["hits"]:
        hits_dict = {}
        if "title" in hit["highlight"]:
            hits_dict["title"] = "".join(hit["highlight"]["title"])
        else:
            hits_dict["title"] = hit["_source"]["title"]

        if "content" in hit["highlight"]:
            hits_dict["content"] = "".join(hit["highlight"]["content"])[:100]
        else:
            hits_dict["content"] = hit["_source"]["content"][:100]
        hits_dict["url"] = hit["_source"]["url"]
        hits_dict["platform"] = hit["_source"]["platform"]
        hits_dict["update_time"] = hit["_source"]["update_time"]
        hits_dict["score"] = hit["_score"]
        hit_list.append(hits_dict)

    return jsonify(data={"data_info":hit_list,
                         "keyword":key_words,
                         "total":total_nums,
                         "page":page,
                         "page_nums":page_nums,
                         "last_seconds":last_seconds,
                         "news_counts": news_counts,
                         "top_search":top_search
                         }
                   )





