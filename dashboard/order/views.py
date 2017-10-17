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
    # Subclass float with custom repr?
        return fakefloat(o)
    elif isinstance(o, bytearray):
        # Subclass float with custom repr?
        return str(o)
    elif isinstance(o,datetime.datetime):
        return o.strftime("%Y-%m-%d %H:%M:%S")
    raise TypeError(repr(o) + " is not JSON serializable")

def getPurchasedUserCountPerOrder(request):
    sql = \
        'select count(distinct pin),\'today\' type from order_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') = DATE_FORMAT(date_sub(now(),INTERVAL 24*1 HOUR),\'%Y-%m-%d\')'\
        'union '\
        'select count(distinct pin),\'yesterday\' type from order_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') = DATE_FORMAT(date_sub(now(),INTERVAL 24*2 HOUR),\'%Y-%m-%d\')'\
        'union '\
        'select count(distinct pin),\'_7daysago\' type from order_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') = DATE_FORMAT(date_sub(now(),INTERVAL 24*8 HOUR),\'%Y-%m-%d\')'\
        'union '\
        'select count(distinct pin),\'_30daysago\' type from order_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') = DATE_FORMAT(date_sub(now(),INTERVAL 24*31 HOUR),\'%Y-%m-%d\')'
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    pin_today = int(0.0 if result[0][0] == None else result[0][0])
    pin_yesterday = int(0.0 if result[1][0] == None else result[1][0])
    pin_7daysago = int(0.0 if result[2][0] == None else result[2][0])
    pin_30daysago = int(0.0 if result[3][0] == None else result[3][0])

    rate_yesterday =  ('N/A' if pin_yesterday ==0.0  else (pin_today-pin_yesterday)*1.0/pin_yesterday)
    rate_7daysago = ('N/A' if pin_7daysago ==0.0  else (pin_today-pin_7daysago)*1.0/pin_7daysago)
    rate_30daysago = ('N/A' if pin_30daysago ==0.0  else (pin_today-pin_30daysago)*1.0/pin_30daysago)

    jsondata={'pin_today': pin_today,'rate_yesterday':rate_yesterday,'rate_7daysago':rate_7daysago,'rate_30daysago':rate_30daysago}
    jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据

    return HttpResponse(jsondata)
def getRevenuePerOrder(request):
    sql = \
        'select sum(pay_amount/100)/count(order_id) ,\'today\' type from order_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') = DATE_FORMAT(date_sub(now(),INTERVAL 24*1 HOUR),\'%Y-%m-%d\') '\
        'union '\
        'select sum(pay_amount/100)/count(order_id),\'yesterday\' type from order_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') = DATE_FORMAT(date_sub(now(),INTERVAL 24*2 HOUR),\'%Y-%m-%d\')'\
        'union '\
        'select sum(pay_amount/100)/count(order_id),\'_7daysago\' type from order_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') = DATE_FORMAT(date_sub(now(),INTERVAL 24*8 HOUR),\'%Y-%m-%d\')'\
        'union '\
        'select sum(pay_amount/100)/count(order_id),\'_30daysago\' type from order_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') = DATE_FORMAT(date_sub(now(),INTERVAL 24*31 HOUR),\'%Y-%m-%d\')'
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    revenue_today = float(0.0 if result[0][0] == None else result[0][0])
    revenue_yesterday = float(0.0 if result[1][0] == None else result[1][0])
    revenue_7daysago = float(0.0 if result[2][0] == None else result[2][0])
    revenue_30daysago =  float(0.0 if result[3][0] == None else result[3][0])

    rate_yesterday =  ('N/A' if revenue_yesterday ==0.0  else (revenue_today-revenue_yesterday)*1.0/revenue_yesterday)
    rate_7daysago = ('N/A' if revenue_7daysago ==0.0  else (revenue_today-revenue_7daysago)*1.0/revenue_7daysago)
    rate_30daysago = ('N/A' if revenue_30daysago ==0.0  else (revenue_today-revenue_30daysago)*1.0/revenue_30daysago)

    jsondata={'revenue_today': revenue_today,'rate_yesterday':rate_yesterday,'rate_7daysago':rate_7daysago,'rate_30daysago':rate_30daysago}
    jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据

    return HttpResponse(jsondata)

def getRevenue(request):
    sql = \
        'select sum(pay_amount/100),\'today\' type from order_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') = DATE_FORMAT(date_sub(now(),INTERVAL 24*1 HOUR),\'%Y-%m-%d\') and status_code=28'\
        'union '\
        'select sum(pay_amount/100),\'yesterday\' type from order_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') = DATE_FORMAT(date_sub(now(),INTERVAL 24*2 HOUR),\'%Y-%m-%d\')  and status_code=28'\
        'union '\
        'select sum(pay_amount/100),\'_7daysago\' type from order_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') = DATE_FORMAT(date_sub(now(),INTERVAL 24*8 HOUR),\'%Y-%m-%d\')  and status_code=28'\
        'union '\
        'select sum(pay_amount/100),\'_30daysago\' type from order_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') = DATE_FORMAT(date_sub(now(),INTERVAL 24*31 HOUR),\'%Y-%m-%d\')  and status_code=28'
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()

    revenue_today = float(0.0 if result[0][0] == None else result[0][0])
    revenue_yesterday = float(0.0 if result[1][0] == None else result[1][0])
    revenue_7daysago = float(0.0 if result[2][0] == None else result[2][0])
    revenue_30daysago =  float(0.0 if result[3][0] == None else result[3][0])

    rate_yesterday =  ('N/A' if revenue_yesterday ==0.0  else (revenue_today-revenue_yesterday)*1.0/revenue_yesterday)
    rate_7daysago = ('N/A' if revenue_7daysago ==0.0  else (revenue_today-revenue_7daysago)*1.0/revenue_7daysago)
    rate_30daysago = ('N/A' if revenue_30daysago ==0.0  else (revenue_today-revenue_30daysago)*1.0/revenue_30daysago)

    jsondata={'revenue_today': revenue_today,'rate_yesterday':rate_yesterday,'rate_7daysago':rate_7daysago,'rate_30daysago':rate_30daysago}
    jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据

    return HttpResponse(jsondata)

def getPurchasedUserCountPerOrderInPeriod(request):
    stt = request.GET.get('stt')
    edt = request.GET.get('edt')
    uc = request.GET.get('uc')
    src = request.GET.get('src')

    sql = ' select count(DISTINCT oi.pin),date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') d from order_info oi '\
        ' left JOIN user_channel uc '\
        ' on oi.pin=uc.pin '\
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') BETWEEN %(stt)s and %(edt)s '\
        ' and status_code = 28 '
    if src != None and len(src)>0:
        'and lower(oi.source) =lower(\''+src+'\')'
    if uc != None and len(uc)>0:
        sql = sql+' and lower(uc.channel) =lower(\''+uc+'\')'
    sql = sql + ' group by d'

    cursor = connections['logdb_fdl'].cursor()
    cursor.execute(sql,{'stt':stt,'edt':edt})
    result = cursor.fetchall()

    data_dict=v4.get_data_dic_templete(stt,edt)
    for res in result:
        data_dict[str(res[1])]=res[0]

    data_list = sorted(data_dict.iteritems(), key=lambda d:d[0])
    res_value=[]
    res_datetime=[]
    for i in range(len(data_list)):
        res_value.append(data_list[i][1])
        res_datetime.append(data_list[i][0])
    print res_value
    print res_datetime
    jsondata={'datetime':res_datetime,'data':res_value}
    jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据
    print jsondata
    return HttpResponse(jsondata)

def getRevenuePerOrderInPeriod(request):
    stt = request.GET.get('stt')
    edt = request.GET.get('edt')
    uc = request.GET.get('uc')
    src = request.GET.get('src')

    sql = ' select sum(pay_amount/100)/count(order_id),date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') d from order_info oi '\
        ' left JOIN user_channel uc '\
        ' on oi.pin=uc.pin '\
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') BETWEEN %(stt)s and %(edt)s '\
        ' and status_code = 28 '
    if src != None and len(src)>0:
        'and lower(oi.source) =lower(\''+src+'\')'
    if uc != None and len(uc)>0:
        sql = sql+' and lower(uc.channel) =lower(\''+uc+'\')'
    sql = sql + ' group by d'

    cursor = connections['logdb_fdl'].cursor()

    cursor.execute(sql,{'stt':stt,'edt':edt})
    result = cursor.fetchall()

    data_dict=v4.get_data_dic_templete(stt,edt)
    for res in result:
        data_dict[str(res[1])]=res[0]

    data_list = sorted(data_dict.iteritems(), key=lambda d:d[0])
    res_value=[]
    res_datetime=[]
    for i in range(len(data_list)):
        res_value.append(data_list[i][1])
        res_datetime.append(data_list[i][0])
    print res_value
    print res_datetime
    jsondata={'datetime':res_datetime,'data':res_value}
    jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据
    print jsondata
    return HttpResponse(jsondata)

def getRevenueInPeriod(request):

    stt = request.GET.get('stt')
    edt = request.GET.get('edt')
    uc = request.GET.get('uc')
    src = request.GET.get('src')

    sql = ' select sum(pay_amount/100),date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') d from order_info oi '\
        ' left JOIN user_channel uc '\
        ' on oi.pin=uc.pin '\
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') BETWEEN %(stt)s and %(edt)s '\
        ' and status_code = 28 '
    if src != None and src != '' and len(src)>0:
        sql = sql + 'and lower(oi.source) =lower(\''+src+'\')'
    if uc != None and len(uc)>0:
        sql = sql+' and lower(uc.channel) =lower(\''+uc+'\')'
    sql = sql + ' group by d'

    cursor = connections['logdb_fdl'].cursor()
    cursor.execute(sql,{'stt':stt,'edt':edt})
    result = cursor.fetchall()

    data_dict=v4.get_data_dic_templete(stt,edt)
    for res in result:
        data_dict[str(res[1])]=res[0]

    data_list = sorted(data_dict.iteritems(), key=lambda d:d[0])
    res_value=[]
    res_datetime=[]
    for i in range(len(data_list)):
        res_value.append(data_list[i][1])
        res_datetime.append(data_list[i][0])
    print res_value
    print res_datetime
    jsondata={'datetime':res_datetime,'data':res_value}
    jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据
    print jsondata
    return HttpResponse(jsondata)


def getRevenueByPlatform(request):
    stt = request.GET.get('stt')
    edt = request.GET.get('edt')
    channel = request.GET.get('channel')
    sql = \
        'select sum(pay_amount/100),sd.source src from order_info oi '\
        ' inner join user_channel uc '\
        ' on oi.pin=uc.pin '\
        ' right join dim.source_dim sd '\
        ' on lower(oi.source)=lower(sd.source) '\
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') BETWEEN %(stt)s and %(edt)s '\
        ' and oi.status_code=28 '\

    if channel != None and len(channel) >0 and channel !='':
        sql = sql +' and uc.channel=\''+channel+'\' '\

    sql =  sql + ' group by src '\

    cursor = connections['logdb_fdl'].cursor()
    cursor.execute(sql,{'stt':stt,'edt':edt})
    result = cursor.fetchall()

    print result

    data=[]
    for res in result:
        data_dic={}
        data_dic['name']=res[1]
        data_dic['value']=res[0]
        data.append(data_dic)

    jsondata={'data': data}
    jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据

    return HttpResponse(jsondata)


def getPaymentFailure(request):
    stt = request.GET.get('stt')
    edt = request.GET.get('edt')
    src = request.GET.get('src')
    sql = 'select count(order_id),\'succeed\' type from order_info oi '\
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') BETWEEN %(stt)s and %(edt)s '\
        ' and status_code=28 '

    if src != None and src !='' and len(src) >0:
        sql = sql + ' and source=\''+src+'\''
    sql = sql + ' union '\
    ' select count(order_id),\'failed\' type from order_info oi '\
    ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') BETWEEN %(stt)s and %(edt)s '\
    ' and status_code in(-1,21,27) '

    if src != None and src !='' and len(src) >0:
        sql = sql + ' and source=\''+src+'\''


    cursor = connections['logdb_fdl'].cursor()
    cursor.execute(sql,{'stt':stt,'edt':edt})
    result = cursor.fetchall()

    data=[]
    for res in result:
        data_dic={}
        data_dic['name']=res[1]
        data_dic['value']=res[0]
        data.append(data_dic)



    jsondata={'data': data}
    jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据

    return HttpResponse(jsondata)


def getOuc(request):
    stt = request.GET.get('stt')
    edt = request.GET.get('edt')
    src = request.GET.get('src')
    channel = request.GET.get('channel')
    sql = 'select count(distinct oi.pin),\'ouc\' type ,date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') d from order_info oi ' \
          'left join user_channel uc on oi.pin=uc.pin '\
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') BETWEEN %(stt)s and %(edt)s '\
        ' and status_code = 28 '\

    if src != None and src !='' and len(src) >0:
        sql = sql + ' and oi.source=\''+src+'\''
    if channel != None and channel !='' and len(channel) >0:
        sql = sql + ' and channel=\''+channel+'\''

    sql = sql + ' group by d'

    cursor = connections['logdb_fdl'].cursor()
    cursor.execute(sql,{'stt':stt,'edt':edt})
    result = cursor.fetchall()

    data_dict=v4.get_data_dic_templete(stt,edt)

    for res in result:
        data_dict[str(res[2])]=res[0]

    data_list = sorted(data_dict.iteritems(), key=lambda d:d[0])
    res_value=[]
    res_datetime=[]
    for i in range(len(data_list)):
        res_value.append(data_list[i][1])
        res_datetime.append(data_list[i][0])
    jsondata={'data': res_value,'datetime':res_datetime}
    jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据

    return HttpResponse(jsondata)


def getOic(request):
    stt = request.GET.get('stt')
    edt = request.GET.get('edt')
    src = request.GET.get('src')
    channel = request.GET.get('channel')
    sql = 'select count(oi.order_id),\'oic\' type ,date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') d from order_info oi '\
        'inner join order_sub_info osi '\
        'on oi.order_no = osi.order_no '\
        'inner join order_sub_detail osd '\
        'on osi.sub_order_no = osd.sub_order_no '\
        'inner join user_channel uc '\
        'on oi.pin=uc.pin '\
        'where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') BETWEEN %(stt)s and %(edt)s '
    sql = sql + 'and oi.status_code = 28 '

    if src != None and src !='' and len(src) >0:
        sql = sql + ' and oi.source=\''+src+'\''
    if channel != None and channel !='' and len(channel) >0:
        sql = sql + ' and channel=\''+channel+'\''

    sql = sql + ' group by d'

    cursor = connections['logdb_fdl'].cursor()
    cursor.execute(sql,{'stt':stt,'edt':edt})
    result = cursor.fetchall()

    data_dict=v4.get_data_dic_templete(stt,edt)

    for res in result:
        data_dict[str(res[2])]=res[0]

    data_list = sorted(data_dict.iteritems(), key=lambda d:d[0])
    res_value=[]
    res_datetime=[]
    for i in range(len(data_list)):
        res_value.append(data_list[i][1])
        res_datetime.append(data_list[i][0])
    jsondata={'data': res_value,'datetime':res_datetime}
    jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据

    return HttpResponse(jsondata)

def getOc(request):
    stt = request.GET.get('stt')
    edt = request.GET.get('edt')
    src = request.GET.get('src')
    channel = request.GET.get('channel')
    sql = ' select count(oi.order_id),\'oc\' type ,date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') d from order_info oi '\
        ' inner join user_channel uc '\
        ' on oi.pin=uc.pin ' \
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') BETWEEN %(stt)s and %(edt)s '
    sql = sql + 'and oi.status_code = 28 '

    if src != None and src !='' and len(src) >0:
        sql = sql + ' and oi.source=\''+src+'\''
    if channel != None and channel !='' and len(channel) >0:
        sql = sql + ' and channel=\''+channel+'\''

    sql = sql + ' group by d'

    cursor = connections['logdb_fdl'].cursor()
    cursor.execute(sql,{'stt':stt,'edt':edt})
    result = cursor.fetchall()

    data_dict=v4.get_data_dic_templete(stt,edt)

    for res in result:
        data_dict[str(res[2])]=res[0]

    data_list = sorted(data_dict.iteritems(), key=lambda d:d[0])
    res_value=[]
    res_datetime=[]
    for i in range(len(data_list)):
        res_value.append(data_list[i][1])
        res_datetime.append(data_list[i][0])
    jsondata={'data': res_value,'datetime':res_datetime}
    jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据

    return HttpResponse(jsondata)

def getOr(request):
    stt = request.GET.get('stt')
    edt = request.GET.get('edt')
    src = request.GET.get('src')
    channel = request.GET.get('channel')
    sql = ' select sum(oi.pay_amount/100),\'or\' type ,date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') d from order_info oi '\
        ' inner join user_channel uc '\
        ' on oi.pin=uc.pin ' \
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') BETWEEN %(stt)s and %(edt)s '
    sql = sql + 'and oi.status_code = 28 '

    if src != None and src !='' and len(src) >0:
        sql = sql + ' and oi.source=\''+src+'\''
    if channel != None and channel !='' and len(channel) >0:
        sql = sql + ' and channel=\''+channel+'\''

    sql = sql + ' group by d'

    cursor = connections['logdb_fdl'].cursor()
    cursor.execute(sql,{'stt':stt,'edt':edt})
    result = cursor.fetchall()

    data_dict=v4.get_data_dic_templete(stt,edt)

    for res in result:
        data_dict[str(res[2])]=res[0]

    data_list = sorted(data_dict.iteritems(), key=lambda d:d[0])
    res_value=[]
    res_datetime=[]
    for i in range(len(data_list)):
        res_value.append(data_list[i][1])
        res_datetime.append(data_list[i][0])
    jsondata={'data': res_value,'datetime':res_datetime}
    jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据

    return HttpResponse(jsondata)

def getOac(request):
    stt = request.GET.get('stt')
    edt = request.GET.get('edt')
    src = request.GET.get('src')
    channel = request.GET.get('channel')
    sql = ' select count(oi.order_id)/count(distinct oi.order_id),\'oac\' type ,date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') d from order_info oi '\
        ' inner join order_sub_info osi '\
        ' on oi.order_no = osi.order_no '\
        ' inner join order_sub_detail osd '\
        ' on osi.sub_order_no = osd.sub_order_no '\
        ' inner join user_channel uc '\
        ' on oi.pin=uc.pin' \
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') BETWEEN %(stt)s and %(edt)s '
    sql = sql + 'and oi.status_code = 28 '

    if src != None and src !='' and len(src) >0:
        sql = sql + ' and oi.source=\''+src+'\''
    if channel != None and channel !='' and len(channel) >0:
        sql = sql + ' and channel=\''+channel+'\''

    sql = sql + ' group by d'

    cursor = connections['logdb_fdl'].cursor()
    cursor.execute(sql,{'stt':stt,'edt':edt})
    result = cursor.fetchall()

    data_dict=v4.get_data_dic_templete(stt,edt)

    for res in result:
        data_dict[str(res[2])]=res[0]
        print res[0],',',res[1]

    data_list = sorted(data_dict.iteritems(), key=lambda d:d[0])
    res_value=[]
    res_datetime=[]
    for i in range(len(data_list)):
        res_value.append(data_list[i][1])
        res_datetime.append(data_list[i][0])
    jsondata={'data': res_value,'datetime':res_datetime}
    jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据

    return HttpResponse(jsondata)

def getItemDataofYesterday(request):
    sql = 'select * from ( '\
        ' select count(order_id) c,\'oc_today\' d from order_info oi '\
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') = date_format(date_sub(now(),interval 7+24*1 HOUR),\'%Y-%m-%d\') '\
        ' union '\
        ' select count(order_id) c,\'oc_yesterday\' d from order_info oi '\
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') = date_format(date_sub(now(),interval 7+24*2 HOUR),\'%Y-%m-%d\') '\
        ' and oi.status_code = 28 '\
        ' union '\
        ' select count(order_id) c,\'oc_7daysago\' d from order_info oi '\
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') = date_format(date_sub(now(),interval 7+24*8 HOUR),\'%Y-%m-%d\') '\
        ' and oi.status_code = 28 '\
        ' union '\
        ' select count(order_id) c,\'oc_30daysago\' d from order_info oi '\
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') = date_format(date_sub(now(),interval 7+24*31 HOUR),\'%Y-%m-%d\') '\
        ' and oi.status_code = 28 '\
        ' union '\
        ' select count(oi.order_id) c,\'oic_today\' d from order_info oi '\
        ' inner join order_sub_info osi '\
        ' on oi.order_no = osi.order_no '\
        ' inner join order_sub_detail osd '\
        ' on osi.sub_order_no = osd.sub_order_no '\
        ' inner join user_channel uc '\
        ' on oi.pin=uc.pin '\
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') = date_format(date_sub(now(),interval 7+24*1 HOUR),\'%Y-%m-%d\') '\
        ' and oi.status_code = 28 '\
        ' union '\
        ' select count(oi.order_id) c,\'oic_yesterday\' d from order_info oi '\
        ' inner join order_sub_info osi '\
        ' on oi.order_no = osi.order_no '\
        ' inner join order_sub_detail osd '\
        ' on osi.sub_order_no = osd.sub_order_no '\
        ' inner join user_channel uc '\
        ' on oi.pin=uc.pin '\
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') = date_format(date_sub(now(),interval 7+24*2 HOUR),\'%Y-%m-%d\') '\
        ' and oi.status_code = 28 '\
        ' union '\
        ' select count(oi.order_id) c,\'oic_7daysago\' d from order_info oi '\
        ' inner join order_sub_info osi '\
        ' on oi.order_no = osi.order_no '\
        ' inner join order_sub_detail osd '\
        ' on osi.sub_order_no = osd.sub_order_no '\
        ' inner join user_channel uc '\
        ' on oi.pin=uc.pin '\
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') = date_format(date_sub(now(),interval 7+24*8 HOUR),\'%Y-%m-%d\') '\
        ' and oi.status_code = 28 '\
        ' union '\
        ' select count(oi.order_id) c,\'oic_30daysago\' d from order_info oi '\
        ' inner join order_sub_info osi '\
        ' on oi.order_no = osi.order_no '\
        ' inner join order_sub_detail osd '\
        ' on osi.sub_order_no = osd.sub_order_no '\
        ' inner join user_channel uc '\
        ' on oi.pin=uc.pin '\
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') = date_format(date_sub(now(),interval 7+24*31 HOUR),\'%Y-%m-%d\') '\
        ' and oi.status_code = 28 '\
        ' union '\
        ' select count(oi.order_id)/count(distinct oi.order_id) c,\'oac_today\' d from order_info oi '\
        ' inner join order_sub_info osi '\
        ' on oi.order_no = osi.order_no '\
        ' inner join order_sub_detail osd '\
        ' on osi.sub_order_no = osd.sub_order_no '\
        ' inner join user_channel uc '\
        ' on oi.pin=uc.pin '\
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') = date_format(date_sub(now(),interval 7+24*1 HOUR),\'%Y-%m-%d\') '\
        ' and oi.status_code = 28 '\
        ' union '\
        ' select count(oi.order_id)/count(distinct oi.order_id) c,\'oac_yesterday\' d from order_info oi '\
        ' inner join order_sub_info osi '\
        ' on oi.order_no = osi.order_no '\
        ' inner join order_sub_detail osd '\
        ' on osi.sub_order_no = osd.sub_order_no '\
        ' inner join user_channel uc '\
        ' on oi.pin=uc.pin '\
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') = date_format(date_sub(now(),interval 7+24*2 HOUR),\'%Y-%m-%d\') '\
        ' and oi.status_code = 28 '\
        ' union '\
        ' select count(oi.order_id)/count(distinct oi.order_id) c,\'oac_7daysago\' d from order_info oi '\
        ' inner join order_sub_info osi '\
        ' on oi.order_no = osi.order_no '\
        ' inner join order_sub_detail osd '\
        ' on osi.sub_order_no = osd.sub_order_no '\
        ' inner join user_channel uc '\
        ' on oi.pin=uc.pin '\
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') = date_format(date_sub(now(),interval 7+24*8 HOUR),\'%Y-%m-%d\') '\
        ' and oi.status_code = 28 '\
        ' union '\
        ' select count(oi.order_id)/count(distinct oi.order_id) c,\'oac_30daysago\' d from order_info oi '\
        ' inner join order_sub_info osi '\
        ' on oi.order_no = osi.order_no '\
        ' inner join order_sub_detail osd '\
        ' on osi.sub_order_no = osd.sub_order_no '\
        ' inner join user_channel uc '\
        ' on oi.pin=uc.pin '\
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') = date_format(date_sub(now(),interval 7+24*31 HOUR),\'%Y-%m-%d\') '\
        ' and oi.status_code = 28 '\
        ' union '\
        ' select count(distinct pin) c, \'customer\' d from order_info oi '\
        ' where date_format(date_sub(oi.create_time,interval 7 HOUR),\'%Y-%m-%d\') = date_format(date_sub(now(),interval 7+24*1 HOUR),\'%Y-%m-%d\') '\
        ' )t '

    cursor = connections['logdb_fdl'].cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    data_dict={}
    for res in result:
        data_dict[str(res[1])] = res[0]

    print data_dict
    oac_30daysago = float(0.0 if data_dict['oac_30daysago'] == None else data_dict['oac_30daysago'])
    oac_7daysago = float(0.0 if data_dict['oac_7daysago'] == None else data_dict['oac_7daysago'])
    oac_yesterday = float(0.0 if data_dict['oac_yesterday'] == None else data_dict['oac_yesterday'])
    oac_today = float(0 if data_dict['oac_today'] == None else data_dict['oac_today'])

    oc_30daysago = float(0.0 if data_dict['oc_30daysago'] == None else data_dict['oc_30daysago'])
    oc_7daysago = float(0.0 if data_dict['oc_7daysago'] == None else data_dict['oc_7daysago'])
    oc_yesterday = float(0.0 if data_dict['oc_yesterday'] == None else data_dict['oc_yesterday'])
    oc_today = float(0.0 if data_dict['oc_today'] == None else data_dict['oc_today'])

    oic_30daysago = float(0.0 if data_dict['oic_30daysago'] == None else data_dict['oic_30daysago'])
    oic_7daysago = float(0.0 if data_dict['oic_7daysago'] == None else data_dict['oic_7daysago'])
    oic_yesterday = float(0.0 if data_dict['oic_yesterday'] == None else data_dict['oic_yesterday'])
    oic_today = float(0.0 if data_dict['oic_today'] == None else data_dict['oic_today'])

    customer = int(0 if data_dict['customer'] == None else data_dict['customer'])

    oac_rate_yesterday =  ('N/A' if oac_yesterday == 0  else (oac_today-oac_yesterday)*1.0/oac_yesterday)
    oac_rate_7daysago = ('N/A' if oac_7daysago == 0  else (oac_today-oac_7daysago)*1.0/oac_7daysago)
    oac_rate_30daysago = ('N/A' if oac_30daysago == 0  else (oac_today-oac_30daysago)*1.0/oac_30daysago)

    oc_rate_yesterday =  ('N/A' if oc_yesterday == 0  else (oc_today-oc_yesterday)*1.0/oc_yesterday)
    oc_rate_7daysago = ('N/A' if oc_7daysago == 0  else (oc_today-oc_7daysago)*1.0/oc_7daysago)
    oc_rate_30daysago = ('N/A' if oc_30daysago == 0  else (oc_today-oc_30daysago)*1.0/oc_30daysago)

    oic_rate_yesterday =  ('N/A' if oic_yesterday == 0  else (oic_today-oic_yesterday)*1.0/oic_yesterday)
    oic_rate_7daysago = ('N/A' if oic_7daysago == 0  else (oic_today-oic_7daysago)*1.0/oic_7daysago)
    oic_rate_30daysago = ('N/A' if oic_30daysago == 0  else (oic_today-oic_30daysago)*1.0/oic_30daysago)


    jsondata={'oac_rate_yesterday': oac_rate_yesterday,'oac_rate_7daysago':oac_rate_7daysago,'oac_rate_30daysago':oac_rate_30daysago,
              'oc_rate_yesterday':oc_rate_yesterday,'oc_rate_7daysago':oc_rate_7daysago,'oc_rate_30daysago':oc_rate_30daysago,
              'oic_rate_yesterday':oic_rate_yesterday,'oic_rate_7daysago':oic_rate_7daysago,'oic_rate_30daysago':oic_rate_30daysago,
              'customer':customer,'oic_today':oic_today,'oac_today':oac_today,'oc_today':oc_today
              }
    jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据

    return HttpResponse(jsondata)

def getTopItems(request):
    stt = request.GET.get('stt')
    edt = request.GET.get('edt')
    top = request.GET.get('top')
    cname = request.GET.get('cname')
    brand = request.GET.get('brand')

    sql = ' select sum(sale_qtty) s,osd.spu,si.main_title,sii.img_path,ci.category_name,di.nickname from order_sub_detail osd '\
    ' inner join designer_prod_mapping dpm on osd.spu=dpm.spu '\
    ' inner join spu_category_mapping_info scmi on osd.spu = scmi.spu '\
    ' inner JOIN category_info ci on scmi.category_id= ci.category_id '\
    ' inner join spu_img_info sii ON sii.spu=osd.spu '\
    ' inner join spu_info si on si.spu = osd.spu '\
    ' inner join designer_info di on di.designer_id = dpm.designer_id '\
    ' inner join order_sub_info osi on osi.sub_order_no = osd.sub_order_no '\
    ' where 1=1 status_code = 28 '
    if cname != None and cname !='' and len(cname) >0:
        sql = sql + ' and ci.category_name = \''+cname+'\''
    if brand != None and brand !='' and len(brand) >0:
        sql = sql + '  and di.nickname =  \''+brand+'\''

    sql = sql + ' and date_format(date_sub(osd.create_time,interval 7 HOUR),\'%Y-%m-%d\') BETWEEN %(stt)s and %(edt)s '\
    ' group by osd.spu order by s asc '

    if top != None and top !='' and len(top) >0:
        sql = sql + ' limit '+top


    cursor = connection.cursor()
    cursor.execute(sql,{'stt':stt,'edt':edt})
    result = cursor.fetchall()

    result_dict_list=[]
    for res in result:
        _dict={}
        _dict['sale_qtty']=res[0]
        _dict['spu']=res[1]
        _dict['main_title']=res[2]
        _dict['img_url']=res[3]
        _dict['cname']=res[4]
        _dict['nickname']=res[5]
        result_dict_list.append(_dict)


    print result
    jsondata={'result':result_dict_list}
    jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据

    return HttpResponse(jsondata)

def getTopSale(request):
    stt = request.GET.get('stt')
    edt = request.GET.get('edt')
    top = request.GET.get('top')
    cname = request.GET.get('cname')
    brand = request.GET.get('brand')
    sql=' select * from ('
    sql = sql + ' select sum(pay_amount/100) s,osd.spu,si.main_title,sii.img_path,ci.category_name,di.nickname from order_sub_detail osd '\
    ' inner join designer_prod_mapping dpm on osd.spu=dpm.spu '\
    ' inner join spu_category_mapping_info scmi on osd.spu = scmi.spu '\
    ' inner JOIN category_info ci on scmi.category_id= ci.category_id '\
    ' inner join spu_img_info sii ON sii.spu=osd.spu '\
    ' inner join spu_info si on si.spu = osd.spu '\
    ' inner join designer_info di on di.designer_id = dpm.designer_id '\
    ' where 1=1 '
    if cname != None and cname !='' and len(cname) >0:
        sql = sql + ' and ci.category_name = \''+cname+'\''

    if brand != None and brand !='' and len(brand) >0:
        sql = sql + '  and di.nickname =  \''+brand+'\''

    sql = sql + ' and date_format(date_sub(osd.create_time,interval 7 HOUR),\'%Y-%m-%d\') BETWEEN %(stt)s and %(edt)s '\
    ' group by osd.spu '
    if cname != None and cname !='' and len(cname) >0:
        sql = sql + ' ,cname '
    sql = sql +' order by s desc '

    if top != None and top !='' and len(top) >0:
        sql = sql + ' limit '+top

    sql = sql +' )t order by t.s asc'
    cursor = connection.cursor()
    cursor.execute(sql,{'stt':stt,'edt':edt})
    result = cursor.fetchall()

    result_dict_list=[]
    for res in result:
        _dict={}
        _dict['sale_amount']=res[0]
        _dict['spu']=res[1]
        _dict['main_title']=res[2]
        _dict['img_url']=res[3]
        _dict['cname']=res[4]
        _dict['nickname']=res[5]
        result_dict_list.append(_dict)


    print result
    jsondata={'result':result_dict_list}
    jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据

    return HttpResponse(jsondata)

