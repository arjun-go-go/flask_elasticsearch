# -*- coding: utf-8 -*-
# @Time    : 18-9-28 上午9:19
# @Author  : Arjun

# li = ["aaa","vvv","bbb","ccc","aaa"]
#
# a = ["ccc","aaa"]
#
# print(set(li)-set(a))
#
# info_tuple = (("title",10),("aaaa",2))
# for text,we in info_tuple:
#     print(text,we)

# import requests
#
# url = "http://127.0.0.1:5000/api/v1_0/search?s=金融"
#
# res = requests.get(url)
#
# print(res.content.decode("utf-8"))
from redis import StrictRedis
redis_client = StrictRedis(host="127.0.0.1",port=6379,db=2)
# redis_client.incr("news_counts")
top_search = redis_client.zrevrangebyscore("keywords_set","+inf", "-inf",start=0,num=5)
print(top_search)

