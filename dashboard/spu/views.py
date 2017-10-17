# -*- coding:utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from subprocess import Popen, PIPE
from decimal import Decimal
import cPickle
# Create your views here.
from order.models import *
from django.db import connection
from django.db import connections

import json
import datetime
from ga_api import v4


class fakefloat(float):
    def __init__(self, value):
        self._value = value
    def __repr__(self):
        return str(self._value)

def defaultencode(o):
    if isinstance(o, Decimal):
        return fakefloat(o)
    elif isinstance(o, bytearray):
        return str(o)
    elif isinstance(o,datetime.datetime):
        return o.strftime("%Y-%m-%d %H:%M:%S")
    raise TypeError(repr(o) + " is not JSON serializable")

def getCategoryName(request):
    sql = 'select distinct category_name from category_info'
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()

    result_value = [x[0] for x in result]

    jsondata={'result': result_value}
    jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据

    return HttpResponse(jsondata)


