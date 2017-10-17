# -*- coding:utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from subprocess import Popen, PIPE
from decimal import Decimal

# Create your views here.
from order.models import *
from django.db import connection
from django.db import connections
import json
import datetime


class fakefloat(float):
    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return str(self._value)


def defaultencode(o):
    if isinstance(o, Decimal):
        # Subclass float with custom repr?
        return fakefloat(o)
    raise TypeError(repr(o) + " is not JSON serializable")


def index_amount(request):
    '''''No comment'''
    return render(request, 'logdata.html', {})


def get_ammount(request):
    # spu_top_sql = 'select spu,main_title,img_path,c,rownum_zuori,rownum_qianri,c2,case when c2 is null then c else c-c2 end ,cast(rankchange as signed) from tmp.res_pv limit 30'
    spu_top_sql = 'select s.spu,main_title,img_path,count(*) c from rec p inner join spu_info s on p.cspus=s.spu inner join spu_img_info i on p.cspus=i.spu where i.isMain=1 and action =1 group by spu order by c desc limit 30'
    # pv_top_sql = 'select s.spu,main_title,img_path,count(*) c from pv p inner join spu_info s on p.spu=s.spu inner join spu_img_info i on p.spu=i.spu where i.isMain=1 group by spu order by c desc  limit 30'
    pv_top_sql = 'select spu,main_title,img_path,c,rownum_zuori,rownum_qianri,c2,case when c2 is null then c else c-c2 end ,cast(rankchange as signed) from res_pv limit 30'
    daily_top_sql = 'select iid,nname,imgpath,skipType,c_zuori,inc,cast(rankchange as signed) from daily order by inc desc limit 30'
    cursor = connections['logdb_fdl'].cursor()
    cursor.execute(spu_top_sql)
    spu_top = cursor.fetchall()

    cursor.close()

    cursor = connections['logdb_tmp'].cursor()
    cursor.execute(daily_top_sql)
    daily_top = cursor.fetchall()
    cursor.execute(pv_top_sql)
    pv_top = cursor.fetchall()

    today = datetime.date.today()
    day = []
    amount = []
    # print day
    print pv_top


    jsondata = {'spu_top': spu_top, 'pv_top': pv_top, 'rankid': range(1, 20), 'daily_top': daily_top}

    # jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据
    # print jsondata
    return render(request, 'logdata.html', {'jsondata': jsondata})

