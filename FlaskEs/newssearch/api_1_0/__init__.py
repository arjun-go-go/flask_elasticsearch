# -*- coding: utf-8 -*-
# @Time    : 18-9-28 下午3:24
# @Author  : Arjun


from flask import Blueprint

# 创建蓝图对象
api = Blueprint("api_1_0", __name__)

from . import search