# -*- coding:utf-8 -*-

from django.shortcuts import render

# Create your views here.
from django.db import connections

from django.shortcuts import render
from django.http import HttpResponse
import json
from decimal import Decimal
# Create your views here.

from user.models import Info
import datetime
from django.db import connection
from ga_api import v4
from ga_api import Params

params=Params.Params()

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


def getTotalRegisterUserCountInPeriod(request):

    src = request.GET.get('src')
    channel = request.GET.get('channel')
    stt = request.GET.get('stt')
    edt = request.GET.get('edt')

    sql=' select t1.DAY_SHORT_DESC,'\
        ' (' \
        ' select sum(c) from ( '\
        ' select a.DAY_SHORT_DESC d,(case when b.c is null then 0 else b.c end) c'\
        ' from dim.datetime_dim a'\
        ' left join'\
        ' ('\
        ' select count(pin) c,date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') d from user_channel '\
        ' where 1=1 ' \
        ' and date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') between %(stt)s and %(edt)s '

    if channel != None and len(channel)>0:
        c1 = ' and channel =lower(\''+channel+'\')'
        sql=sql+c1
    if src != None and len(src)>0:
        c2 = ' and source =lower(\''+src+'\')'
        sql=sql+c2
    sql=sql+' group by d' \
	' ) b on a.DAY_SHORT_DESC=b.d'\
    ' ) t2'\
    ' where t2.d<=t1.DAY_SHORT_DESC'\
    ' ) from dim.datetime_dim t1 where t1.DAY_SHORT_DESC between %(stt)s and %(edt)s'\


    cursor = connections['logdb_fdl'].cursor()

    cursor.execute(sql,{'stt': stt, 'edt': edt})
    result = cursor.fetchall()
    cursor.close()

    print result

    data_dic = v4.get_data_dic_templete(stt,edt)
    print data_dic
    for res in result:
        #print res[0]+':', str(res[1])
        data_dic[str(res[0])]=res[1]

    #print data_dic
    data_list = sorted(data_dic.iteritems(), key=lambda d:d[0])
    #print data_list
    res_value = []
    res_datetime = []
    for i in range(len(data_list)):
        res_value.append(data_list[i][1])
        res_datetime.append(data_list[i][0])

    jsondata = {'datetime': res_datetime,'data':res_value}

    jsondata = json.dumps(jsondata, sort_keys=True, separators=(',', ': '), default=defaultencode)  # 使用dumps方法格式化数据
    print 'jsondata=',jsondata
    return HttpResponse(jsondata)


def getRegisterUserCount(request):
    sql='select count(pin),\'today\' type from user_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') = DATE_FORMAT(date_sub(now(),INTERVAL 24*1 HOUR),\'%Y-%m-%d\') '\
        'union '\
        'select count(pin),\'yesterday\' type from user_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') = DATE_FORMAT(date_sub(now(),INTERVAL 24*2 HOUR),\'%Y-%m-%d\') '\
        'union '\
        'select count(pin),\'_7daysago\' type from user_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') = DATE_FORMAT(date_sub(now(),INTERVAL 24*8 HOUR),\'%Y-%m-%d\')'\
        'union '\
        'select count(pin),\'_30daysago\' type from user_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') = DATE_FORMAT(date_sub(now(),INTERVAL 24*31 HOUR),\'%Y-%m-%d\')'\
        'union '\
        'select count(pin),\'today\' type from user_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') <= DATE_FORMAT(date_sub(now(),INTERVAL 24*1 HOUR),\'%Y-%m-%d\') '\
        'union '\
        'select count(pin),\'yesterday\' type from user_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') <= DATE_FORMAT(date_sub(now(),INTERVAL 24*2 HOUR),\'%Y-%m-%d\') '\
        'union '\
        'select count(pin),\'_7daysago\' type from user_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') <= DATE_FORMAT(date_sub(now(),INTERVAL 24*8 HOUR),\'%Y-%m-%d\')'\
        'union '\
        'select count(pin),\'_30daysago\' type from user_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') <= DATE_FORMAT(date_sub(now(),INTERVAL 24*31 HOUR),\'%Y-%m-%d\')'

    cursor = connections['logdb_fdl'].cursor()

    cursor.execute(sql)
    count = cursor.fetchall()
    cursor.close()

    count_today = count[0][0]
    count_yesterday = count[1][0]
    count_7daysago = count[2][0]
    count_30daysago = count[3][0]

    count_today_all = count[4][0]
    count_yesterday_all = count[5][0]
    count_7daysago_all = count[6][0]
    count_30daysago_all = count[7][0]

    if count_yesterday == 0:
        rate_yesterday = 'N/A'
    else :rate_yesterday = (count_today-count_yesterday)*1.0/count_yesterday
    if count_7daysago == 0:
        rate_7daysago = 'N/A'
    else :rate_7daysago = (count_today-count_7daysago)*1.0/count_7daysago
    if count_30daysago == 0:
        rate_30daysago = 'N/A'
    else :rate_30daysago = (count_today-count_30daysago)*1.0/count_30daysago


    if count_yesterday_all == 0:
        rate_yesterday_all = 'N/A'
    else :rate_yesterday_all = (count_today_all-count_yesterday_all)*1.0/count_yesterday_all
    if count_7daysago_all == 0:
        rate_7daysago_all = 'N/A'
    else :rate_7daysago_all = (count_today_all-count_7daysago_all)*1.0/count_7daysago_all
    if count_30daysago_all == 0:
        rate_30daysago_all = 'N/A'
    else :rate_30daysago_all = (count_today_all-count_30daysago_all)*1.0/count_30daysago_all




    jsondata = {'count_today': count_today,'rate_yesterday':rate_yesterday,'rate_7daysago':rate_7daysago,'rate_30daysago':rate_30daysago,
                'count_today_all':count_today_all,'rate_yesterday_all':rate_yesterday_all,
                'rate_7daysago_all':rate_7daysago_all,'rate_30daysago_all':rate_30daysago_all}

    jsondata = json.dumps(jsondata, sort_keys=True, separators=(',', ': '), default=defaultencode)  # 使用dumps方法格式化数据
    # print 'jsondata=',jsondata
    return HttpResponse(jsondata)

def getRegisterUserCountInPeriod(request):

    src = request.GET.get('src')
    channel = request.GET.get('channel')
    stt = request.GET.get('stt')
    edt = request.GET.get('edt')

    sql='select count(pin),date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') d from user_channel where 1=1 '\
        'and date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') between %(stt)s and %(edt)s'

    if channel != None and len(channel)>0:
        c1 = ' and lower(channel) =lower(\''+channel+'\')'
        sql=sql+c1
    if src != None and len(src)>0:
        c2 = ' and lower(source) =lower(\''+src+'\')'
        sql=sql+c2

    sql=sql+' group by d'
    print sql
    cursor = connections['logdb_fdl'].cursor()

    cursor.execute(sql,{'stt': stt, 'edt': edt})
    result = cursor.fetchall()
    cursor.close()

    print result

    data_dic = v4.get_data_dic_templete(stt,edt)

    for res in result:
        data_dic[str(res[1])]=res[0]

    data_list = sorted(data_dic.iteritems(), key=lambda d:d[0])

    res_value = []
    res_datetime = []
    for i in range(len(data_list)):
        res_value.append(data_list[i][1])
        res_datetime.append(data_list[i][0])
    jsondata = {'datetime': res_datetime,'data':res_value}

    jsondata = json.dumps(jsondata, sort_keys=True, separators=(',', ': '), default=defaultencode)  # 使用dumps方法格式化数据
    print 'jsondata=',jsondata
    return HttpResponse(jsondata)

def getChannelName(request):
	sql = 'select distinct channel from user_channel'
	cursor = connections['logdb_fdl'].cursor()
	cursor.execute(sql)
	result = cursor.fetchall()

	result_value = [x[0] for x in result]

	jsondata={'result': result_value}
	jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据

	return HttpResponse(jsondata)

def getSpuFunnel(request):
    brand = request.GET.get('brand')
    stt = request.GET.get('stt')
    edt = request.GET.get('edt')

    sql=' select pv.spu,ci.category_name,si.puton_time,`pi`.price/100 price,oap ,'\
        ' count(*) pview,count(DISTINCT `UUID`) uview , t2.atwl,t3.atct,t1.`or`,t1.oc from pv '\
        ' inner join spu_category_mapping_info scmi on scmi.spu = pv.spu '\
        ' inner join category_info ci on scmi.category_id = ci.category_id '\
        ' inner JOIN spu_info si on si.spu = pv.spu '\
        ' inner join prod_info `pi` on `pi`.spu = pv.spu '\
        ' left join (select spu,sum(pay_amount/100)/sum(sale_qtty) oap,sum(pay_amount/100) `or`,sum(sale_qtty) oc from order_sub_detail osd '\
        ' where date_format(date_sub(osd.create_time,interval 7 HOUR),\'%Y-%m-%d\') between %(stt)s and %(edt)s '\
        ' group by spu )t1 on pv.spu = t1.spu '\
        ' left join (select skipId,count(*) atwl FROM wishlist wl '\
        ' where date_format(date_sub(FROM_UNIXTIME(wl.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') between %(stt)s and %(edt)s '\
        ' group by skipId)t2 on pv.spu = t2.skipId '\
        ' left join (select skipId,count(*) atct FROM cart ct '\
        ' where date_format(date_sub(FROM_UNIXTIME(ct.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') between %(stt)s and %(edt)s '\
        ' group by skipId)t3 on pv.spu = t3.skipId '\
        ' left join designer_prod_mapping dpm on dpm.spu = pv.spu '\
        ' left join designer_info di on di.designer_id = dpm.designer_id '\
        ' where date_format(date_sub(FROM_UNIXTIME(pv.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') between %(stt)s and %(edt)s '

    if brand != None and brand !='' and len(brand) >0:
        sql = sql + '  and di.nickname =  \''+brand+'\''

    sql = sql +'group by spu '

    print sql
    cursor = connections['logdb_fdl'].cursor()

    cursor.execute(sql,{'stt': stt, 'edt': edt})
    result = cursor.fetchall()
    cursor.close()


    jsondata = {'result': result}

    jsondata = json.dumps(jsondata, sort_keys=True, separators=(',', ': '), default=defaultencode)  # 使用dumps方法格式化数据
    print 'jsondata=',jsondata
    return HttpResponse(jsondata)

#
# def getUserFunnel(request):
#
#     brand = request.GET.get('brand')
#     stt = request.GET.get('stt')
#     edt = request.GET.get('edt')
#
#     sql=''
#
#     print sql
#     cursor = connections['logdb_fdl'].cursor()
#
#     cursor.execute(sql,{'stt': stt, 'edt': edt})
#     result = cursor.fetchall()
#     cursor.close()
#
#
#     jsondata = {'result': result}
#
#     jsondata = json.dumps(jsondata, sort_keys=True, separators=(',', ': '), default=defaultencode)  # 使用dumps方法格式化数据
#     print 'jsondata=',jsondata
#     return HttpResponse(jsondata)
#
