# -*- coding:utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
import json
from decimal import Decimal
# Create your views here.

from user.models import Info
import datetime
from django.db import connection
from django.db import connections
from ga_api import v4
from ga_api import Params
from firebase_api import bigQuery

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



def get_all_users(request):
    todaysql = 'select count(*) from user_info where datediff(now(),create_time)=0'

    # res = Info.objects.raw(raw_sql)
    # for r in res:
    # 	print r.all_amount;
    # res = Info.objects.all()
    cursor = connection.cursor()

    cursor.execute(todaysql)
    todaycount = cursor.fetchall()
    cursor.close()

    user_count = Info.objects.filter().count()

    return render(request, 'Users.html', {'user_count': user_count,'today_count':todaycount[0][0]})


#已被getFunnel引用
def getWebUserCountTrend(request):
    print 'getWebUserCountTrend'
    stt = request.GET.get('stt')#开始时间
    edt = request.GET.get('edt')#结束时间
    filter = request.GET.get('lp')#落地页路径
    src = request.GET.get('src')#all或web或pc
    #params=Params.Params()

    print id(params)

    if filter == None or filter == '' or len(filter)==0:
        filter = None
    pc_response = None
    h5_response = None
    if src == 'h5':
        h5_response = v4.getUserOfSomePeriod(params,params.h5_ID,stt,edt,filter)
    elif src == 'pc':
        pc_response = v4.getUserOfSomePeriod(params,params.pc_ID,stt,edt,filter)
    elif src == '':
        h5_response = v4.getUserOfSomePeriod(params,params.h5_ID,stt,edt,filter)
        pc_response = v4.getUserOfSomePeriod(params,params.pc_ID,stt,edt,filter)
    else : return HttpResponse('param err')
    #print h5_response
    #print pc_response

    h5_data_dic = v4.get_data_dic_templete(stt,edt)
    pc_data_dic = v4.get_data_dic_templete(stt,edt)

    if h5_response != None and h5_response.get('reports')[0].get('data').get('rows')!= None:
        for res in h5_response.get('reports')[0].get('data').get('rows'):

            r_value = res.get('metrics')[0].get('values')
            c = datetime.datetime.strptime(str(res.get('dimensions')[1]),'%Y%m%d')

            r_date=str(c.strftime('%Y-%m-%d'))#实际存在的日期
            h5_data_dic[r_date]= int(str(r_value[0]))
    if pc_response != None and pc_response.get('reports')[0].get('data').get('rows')!= None:
        for res in pc_response.get('reports')[0].get('data').get('rows'):

            r_value = res.get('metrics')[0].get('values')
            c = datetime.datetime.strptime(str(res.get('dimensions')[1]),'%Y%m%d')

            r_date=str(c.strftime('%Y-%m-%d'))#实际存在的日期

            pc_data_dic[r_date]= int(str(r_value[0]))

    h5_data_list = sorted(h5_data_dic.iteritems(), key=lambda d:d[0])
    pc_data_list = sorted(pc_data_dic.iteritems(), key=lambda d:d[0])

    #print h5_data_list
    #print pc_data_list


    res_value=[]
    res_datetime=[]
    for i in range(len(h5_data_list)):
        res_value.append(h5_data_list[i][1]+pc_data_list[i][1])
        res_datetime.append(h5_data_list[i][0])
    #print res_value
    #print res_datetime

    jsondata = {'datetime': res_datetime, 'data': res_value}
    jsondata = json.dumps(jsondata, sort_keys=True, separators=(',', ': '), default=defaultencode)  # 使用dumps方法格式化数据
    # print jsondata

    response = HttpResponse(jsondata)
    return response


def getWebUserCount(request):
    print 'getWebUserCount'

    #params=Params.Params()
    print id(params)
    webUserCount_dict=v4.getWebUserCount(params)
    count_today=webUserCount_dict.get('count_today')

    count_yesterday=webUserCount_dict.get('count_yesterday')

    #print count_today
    #print count_yesterday
    if count_yesterday==0 :
        rate_yesterday='N/A'
    else :rate_yesterday=(count_today-count_yesterday)*1.0/count_yesterday

    count_7daysago=webUserCount_dict.get('count_7daysago')
    if count_7daysago==0 :
        rate_7daysago='N/A'
    else :rate_7daysago=(count_today-count_7daysago)*1.0/count_7daysago

    count_30daysago=webUserCount_dict.get('count_30daysago')
    if count_30daysago==0 :
        rate_30daysago='N/A'
    else : rate_30daysago=(count_today-count_30daysago)*1.0/count_30daysago

    jsondata = {'count_today': count_today, 'rate_yesterday': rate_yesterday, 'rate_7daysago':rate_7daysago,'rate_30daysago':rate_30daysago}
    jsondata = json.dumps(jsondata, sort_keys=True, separators=(',', ': '), default=defaultencode)  # 使用dumps方法格式化数据
    # print jsondata

    response = HttpResponse(jsondata)
    return response

def getAppUserCountTrend(request):
    print 'getAppUserCountTrend'
    stt=request.GET.get('stt')
    edt=request.GET.get('edt')
    src=request.GET.get('src')
    i_data_dict=v4.get_data_dic_templete(stt,edt)
    a_data_dict=v4.get_data_dic_templete(stt,edt)
    stt=datetime.datetime.strptime(stt,'%Y-%m-%d')
    edt=datetime.datetime.strptime(edt,'%Y-%m-%d')

    stt = str(stt.strftime('%Y%m%d'))
    edt = str(edt.strftime('%Y%m%d'))
    a_response={}
    i_response={}
    if src == None or src=='':
        print 0
        try:i_response = bigQuery.active_user('ios',stt,edt)
        except Exception,e:print (e,'ios err')
        try:a_response = bigQuery.active_user('android',('20161102' if stt<'20161102' else stt),(edt))
        except Exception,e:print (e,'android err')

    elif src=='ios':
        print 1
        try:i_response = bigQuery.active_user('ios',stt,edt)
        except Exception,e:print (e,'ios err')
    elif src =='android':
        print 2
        try:a_response = bigQuery.active_user('android',('20161102' if stt<'20161102' else stt),(edt))
        except Exception,e:print (e,'android err')

    print a_response
    print i_response
    for i in range(len(i_response)):

        dt=i_response[i]['dt']
        uv=i_response[i]['uv']

        dt = datetime.datetime.strptime(dt,'%Y%m%d')
        dt = dt.strftime('%Y-%m-%d')

        i_data_dict[dt]=uv
    for i in range(len(a_response)):

        dt=a_response[i]['dt']
        uv=a_response[i]['uv']

        dt = datetime.datetime.strptime(dt,'%Y%m%d')
        dt = dt.strftime('%Y-%m-%d')

        a_data_dict[dt]=uv

    total_data_dict=v4.get_data_dic_templete(request.GET.get('stt'),request.GET.get('edt'))
    date_keys = total_data_dict.keys()
    for k in date_keys:
        total_data_dict[k]=a_data_dict[k]+i_data_dict[k]

    data_list = sorted(total_data_dict.iteritems(), key=lambda d:d[0])
    res_value=[]
    res_datetime=[]
    for i in range(len(data_list)):
        res_value.append(data_list[i][1])
        res_datetime.append(data_list[i][0])
    print res_value
    print res_datetime
    jsondata={'datetime':res_datetime,'data':res_value}
    jsondata = json.dumps(jsondata, sort_keys=True, separators=(',', ': '), default=defaultencode)  # 使用dumps方法格式化数据
    return  HttpResponse(jsondata)



def getAppUserCount(request):
    print 'getAppUserCount'
    d0=datetime.datetime.strptime(v4.strtoday,'%Y-%m-%d')
    d1=datetime.datetime.strptime(v4.stryesterday,'%Y-%m-%d')
    d7=datetime.datetime.strptime(v4.str_7daysago,'%Y-%m-%d')
    d30=datetime.datetime.strptime(v4.str_30daysago,'%Y-%m-%d')


    d0 = str(d0.strftime('%Y%m%d'))
    d1 = str(d1.strftime('%Y%m%d'))
    d7 = str(d7.strftime('%Y%m%d'))
    d30 = str(d30.strftime('%Y%m%d'))
    #ios某天
    try:i_count_today = bigQuery.active_user('ios',d0,d0)[0]['uv']
    except Exception,e:i_count_today=0
    try:i_count_yesterday = bigQuery.active_user('ios',d1,d1)[0]['uv']
    except Exception,e:i_count_yesterday=0
    try:i_count_7daysago = bigQuery.active_user('ios',d7,d7)[0]['uv']
    except Exception,e:i_count_7daysago=0
    try:i_count_30daysago = bigQuery.active_user('ios',d30,d30)[0]['uv']
    except Exception,e:i_count_30daysago=0
    #android某天
    try:a_count_today = bigQuery.active_user('android',d0,d0)[0]['uv']
    except Exception,e:a_count_today=0
    try:a_count_yesterday = bigQuery.active_user('android',d1,d1)[0]['uv']
    except Exception,e:a_count_yesterday=0
    try:a_count_7daysago = bigQuery.active_user('android',d7,d7)[0]['uv']
    except Exception,e:a_count_7daysago=0
    try:a_count_30daysago = bigQuery.active_user('android',d30,d30)[0]['uv']
    except Exception,e:a_count_30daysago=0

    if i_count_yesterday+a_count_yesterday==0 :
        rate_yesterday='N/A'
    else :rate_yesterday=((i_count_today+a_count_today)-(i_count_yesterday+a_count_yesterday))*1.0/(i_count_yesterday+a_count_yesterday)

    if i_count_7daysago+a_count_7daysago==0 :
        rate_7daysago='N/A'
    else :rate_7daysago=((i_count_today+a_count_today)-(i_count_7daysago+a_count_7daysago))*1.0/(i_count_7daysago+a_count_7daysago)

    if i_count_30daysago+a_count_30daysago==0 :
        rate_30daysago='N/A'
    else : rate_30daysago=((i_count_today+a_count_today)-(i_count_30daysago+a_count_30daysago))*1.0/(i_count_30daysago+a_count_30daysago)

    jsondata = {'count_today': i_count_today+a_count_today, 'rate_yesterday': rate_yesterday, 'rate_7daysago':rate_7daysago,'rate_30daysago':rate_30daysago}
    jsondata = json.dumps(jsondata, sort_keys=True, separators=(',', ': '), default=defaultencode)  # 使用dumps方法格式化数据
    # print jsondata

    response = HttpResponse(jsondata)
    return response


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



def getUserFunnelConversionDataofYesterday(request):
    print 'getTotalUserCount'

    #params=Params.Params()
    print id(params)
    webUserCount_dict=v4.getWebUserCount(params)

    web_count_today=webUserCount_dict.get('count_today')
    web_count_yesterday=webUserCount_dict.get('count_yesterday')
    web_count_7daysago=webUserCount_dict.get('count_7daysago')
    web_count_30daysago=webUserCount_dict.get('count_30daysago')


    try:
        i0 = bigQuery.active_user('ios',str(v4.today.strftime('%Y%m%d')),str(v4.today.strftime('%Y%m%d')))[0]['uv']
    except Exception,e:
        i0 = 0
    try:
        a0 = bigQuery.active_user('android',str(v4.today.strftime('%Y%m%d')),str(v4.today.strftime('%Y%m%d')))[0]['uv']
    except Exception,e:
        a=0
    try:
        i1 = bigQuery.active_user('ios',str(v4.yesterday.strftime('%Y%m%d')),str(v4.yesterday.strftime('%Y%m%d')))[0]['uv']
    except Exception,e:
        i1=0
    try:
        a1 = bigQuery.active_user('android',str(v4.yesterday.strftime('%Y%m%d')),str(v4.yesterday.strftime('%Y%m%d')))[0]['uv']
    except Exception,e:
        a1=0
    try:
        i7 = bigQuery.active_user('ios',str(v4._7daysago.strftime('%Y%m%d')),str(v4._7daysago.strftime('%Y%m%d')))[0]['uv']
    except Exception,e:
        i7=0
    try:
        a7 = bigQuery.active_user('android',str(v4._7daysago.strftime('%Y%m%d')),str(v4._7daysago.strftime('%Y%m%d')))[0]['uv']
    except Exception,e:
        a7=0
    try:
        i30 = bigQuery.active_user('ios',str(v4._30daysago.strftime('%Y%m%d')),str(v4._30daysago.strftime('%Y%m%d')))[0]['uv']
    except Exception,e:
        i30=0
    try:
        a30 = bigQuery.active_user('android',str(v4._30daysago.strftime('%Y%m%d')),str(v4._30daysago.strftime('%Y%m%d')))[0]['uv']
    except Exception,e:
        a30=0

    app_count_today=i0+a0
    app_count_yesterday=i1+a1
    app_count_7daysago=i7+a7
    app_count_30daysago=i30+a30

    today = app_count_today + web_count_today
    yesterday = app_count_yesterday + web_count_yesterday
    _7daysago = app_count_7daysago + web_count_7daysago
    _30daysago = app_count_30daysago + web_count_30daysago

    rate_yesterday = ('N/A' if yesterday == 0 else (today - yesterday)*1.0/yesterday)
    rate_7daysago = ('N/A' if yesterday == 0 else (today - _7daysago)*1.0/_7daysago)
    rate_30daysago = ('N/A' if yesterday == 0 else (today - _30daysago)*1.0/_30daysago)



    sql = 'select count(distinct `UUID`),\'pv_today\' d from pv where date_format(date_sub(FROM_UNIXTIME(pv.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') =date_format(date_sub(now(),interval 7+24*1 hour),\'%Y-%m-%d\') '\
            'union '\
            'select count(distinct `UUID`),\'pv_yesterday\' d from pv where date_format(date_sub(FROM_UNIXTIME(pv.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') =date_format(date_sub(now(),interval 7+24*2 hour),\'%Y-%m-%d\') '\
            'union '\
            'select count(distinct `UUID`),\'pv_7daysago\' d from pv where date_format(date_sub(FROM_UNIXTIME(pv.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') =date_format(date_sub(now(),interval 7+24*8 hour),\'%Y-%m-%d\')  '\
            'union '\
            'select count(distinct `UUID`),\'pv_30daysago\' d from pv where date_format(date_sub(FROM_UNIXTIME(pv.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') =date_format(date_sub(now(),interval 7+24*31 hour),\'%Y-%m-%d\')  '\
            'union '\
            'select count(distinct `UUID`),\'cart_today\' d from cart where date_format(date_sub(FROM_UNIXTIME(cart.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') =date_format(date_sub(now(),interval 7+24*1 hour),\'%Y-%m-%d\')  '\
            'union '\
            'select count(distinct `UUID`),\'cart_yesterday\' d from cart where date_format(date_sub(FROM_UNIXTIME(cart.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') =date_format(date_sub(now(),interval 7+24*2 hour),\'%Y-%m-%d\') '\
            'union '\
            'select count(distinct `UUID`),\'cart_7daysago\' d from cart where date_format(date_sub(FROM_UNIXTIME(cart.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') =date_format(date_sub(now(),interval 7+24*8 hour),\'%Y-%m-%d\')  '\
            'union '\
            'select count(distinct `UUID`),\'cart_30daysago\' d from cart where date_format(date_sub(FROM_UNIXTIME(cart.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') =date_format(date_sub(now(),interval 7+24*31 hour),\'%Y-%m-%d\')  '\
            'union '\
            'select count(distinct `UUID`),\'check_today\' d from _check where date_format(date_sub(FROM_UNIXTIME(_check.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') =date_format(date_sub(now(),interval 7+24*1 hour),\'%Y-%m-%d\')  '\
            'union '\
            'select count(distinct `UUID`),\'check_yesterday\' d from _check where date_format(date_sub(FROM_UNIXTIME(_check.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') =date_format(date_sub(now(),interval 7+24*2 hour),\'%Y-%m-%d\') '\
            'union '\
            'select count(distinct `UUID`),\'check_7daysago\' d from _check where date_format(date_sub(FROM_UNIXTIME(_check.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') =date_format(date_sub(now(),interval 7+24*8 hour),\'%Y-%m-%d\')  '\
            'union '\
            'select count(distinct `UUID`),\'check_30daysago\' d from _check where date_format(date_sub(FROM_UNIXTIME(_check.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') =date_format(date_sub(now(),interval 7+24*31 hour),\'%Y-%m-%d\')  '\
            'union '\
            'select count(distinct `UUID`),\'order_today\' d from _order where date_format(date_sub(FROM_UNIXTIME(_order.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') =date_format(date_sub(now(),interval 7+24*1 hour),\'%Y-%m-%d\')  '\
            'union '\
            'select count(distinct `UUID`),\'order_yesterday\' d from _order where date_format(date_sub(FROM_UNIXTIME(_order.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') =date_format(date_sub(now(),interval 7+24*2 hour),\'%Y-%m-%d\') '\
            'union '\
            'select count(distinct `UUID`),\'order_7daysago\' d from _order where date_format(date_sub(FROM_UNIXTIME(_order.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') =date_format(date_sub(now(),interval 7+24*8 hour),\'%Y-%m-%d\')  '\
            'union '\
            'select count(distinct `UUID`),\'order_30daysago\' d from _order where date_format(date_sub(FROM_UNIXTIME(_order.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') =date_format(date_sub(now(),interval 7+24*31 hour),\'%Y-%m-%d\') '

    cursor = connections['logdb_fdl'].cursor()

    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()

    pv_today = result[0][0]
    pv_yesterday = result[1][0]
    pv_7daysago = result[2][0]
    pv_30daysago = result[3][0]
    pv_rate_yesterday = ('N/A' if pv_yesterday == 0 else (pv_today - pv_yesterday)*1.0/pv_yesterday)
    pv_rate_7daysago = ('N/A' if pv_7daysago == 0 else (pv_today - pv_7daysago)*1.0/pv_7daysago)
    pv_rate_30daysago = ('N/A' if pv_30daysago == 0 else (pv_today - pv_30daysago)*1.0/pv_30daysago)

    cart_today = result[4][0]
    cart_yesterday = result[5][0]
    cart_7daysago = result[6][0]
    cart_30daysago = result[7][0]
    cart_rate_yesterday = ('N/A' if cart_yesterday == 0 else (cart_today - cart_yesterday)*1.0/cart_yesterday)
    cart_rate_7daysago = ('N/A' if cart_7daysago == 0 else (cart_today - cart_7daysago)*1.0/cart_7daysago)
    cart_rate_30daysago = ('N/A' if cart_30daysago == 0 else (cart_today - cart_30daysago)*1.0/cart_30daysago)


    check_today = result[8][0]
    check_yesterday = result[9][0]
    check_7daysago = result[10][0]
    check_30daysago = result[11][0]
    check_rate_yesterday = ('N/A' if check_yesterday == 0 else (check_today - check_yesterday)*1.0/check_yesterday)
    check_rate_7daysago = ('N/A' if check_7daysago == 0 else (check_today - check_7daysago)*1.0/check_7daysago)
    check_rate_30daysago = ('N/A' if check_30daysago == 0 else (check_today - check_30daysago)*1.0/check_30daysago)


    order_today = result[12][0]
    order_yesterday = result[13][0]
    order_7daysago = result[14][0]
    order_30daysago = result[15][0]
    order_rate_yesterday = ('N/A' if order_yesterday == 0 else (order_today - order_yesterday)*1.0/order_yesterday)
    order_rate_7daysago = ('N/A' if order_7daysago == 0 else (order_today - order_7daysago)*1.0/order_7daysago)
    order_rate_30daysago = ('N/A' if order_30daysago == 0 else (order_today - order_30daysago)*1.0/order_30daysago)

    pv_funnel = ('N/A' if today == 0 else (pv_today)*1.0/today)
    cart_funnel = ('N/A' if today == 0 else (cart_today)*1.0/today)
    check_funnel = ('N/A' if today == 0 else (check_today)*1.0/today)
    order_funnel = ('N/A' if today == 0 else (order_today)*1.0/today)
    jsondata = {'total_count': today, 'rate_yesterday': rate_yesterday, 'rate_7daysago':rate_7daysago,'rate_30daysago':rate_30daysago,
                'pv_today':pv_today,'pv_rate_yesterday':pv_rate_yesterday,'pv_rate_7daysago':pv_rate_7daysago,'pv_rate_30daysago':pv_rate_30daysago,
                'cart_today':cart_today,'cart_rate_yesterday':cart_rate_yesterday,'cart_rate_7daysago':cart_rate_7daysago,'cart_rate_30daysago':cart_rate_30daysago,
                'check_today':check_today,'check_rate_yesterday':check_rate_yesterday,'check_rate_7daysago':check_rate_7daysago,'check_rate_30daysago':check_rate_30daysago,
                'order_today':order_today,'order_rate_yesterday':order_rate_yesterday,'order_rate_7daysago':order_rate_7daysago,'order_rate_30daysago':order_rate_30daysago,
                'pv_funnel':pv_funnel,'cart_funnel':cart_funnel,'check_funnel':check_funnel,'order_funnel':order_funnel
    }
    jsondata = json.dumps(jsondata, sort_keys=True, separators=(',', ': '), default=defaultencode)  # 使用dumps方法格式化数据
    # print jsondata

    response = HttpResponse(jsondata)
    return response

def getIOSorAndroidResultDict(stt,edt,type):

    data_dict = v4.get_data_dic_templete(stt,edt)
    #try:
    c_stt = datetime.datetime.strptime(stt,'%Y-%m-%d')
    c_edt = datetime.datetime.strptime(edt,'%Y-%m-%d')
    response = bigQuery.active_user(type,c_stt.strftime('%Y%m%d'),c_edt.strftime('%Y%m%d'))
    delta = datetime.timedelta(days=1)
    i=0
    print response
    #while i <=c_edt:
    for i in range(len(response)):
        #c_stt.strftime("%Y%m%d")
        try:
            d=datetime.datetime.strptime(response[i]['dt'],'%Y%m%d')
            print d
            data_dict[datetime.datetime.strftime(d,'%Y-%m-%d')]=response[i]['uv']
            i=i+1
        except Exception,e:
            print e
            pass
        c_stt += delta

        print data_dict

    return  data_dict
    #except Exception,e:
    #print (e,'at getIOSorAndroidResultDict function')

def getUserFunnelTable(request,src=None,funnel=None,stt=None,edt=None):
    src = request.GET.get('src')
    funnel = request.GET.get('funnel')
    stt = request.GET.get('stt')
    edt = request.GET.get('edt')
    print getUserFunnel(src=src,funnel='total',stt=stt,edt=edt)
    print getUserFunnel(src=src,funnel='pv',stt=stt,edt=edt)
    print getUserFunnel(src=src,funnel='cart',stt=stt,edt=edt)
    print getUserFunnel(src=src,funnel='_check',stt=stt,edt=edt)
    print getUserFunnel(src=src,funnel='_order',stt=stt,edt=edt)

def getUserFunnel(request,src=None,funnel=None,stt=None,edt=None,return_type=0):
    src = request.GET.get('src')
    funnel = request.GET.get('funnel')
    stt = request.GET.get('stt')
    edt = request.GET.get('edt')
    print funnel
    print src
    data_dict = v4.get_data_dic_templete(stt,edt)

    #if (funnel=='total' and stt<'2016-11-02' and src =='android') or (funnel=='total' and stt<'2016-11-02' and src != None and src==''):
    #    return HttpResponse({'android start time cannnot be smaller than 2016-11-02'})


    if funnel == None or (funnel !='pv' and funnel !='cart' and funnel !='_check' and funnel !='_order'):
        if funnel == 'total':
            if src == None or src=='':
                h5_response = v4.getUserOfSomePeriod(params,params.h5_ID,stt,edt)
                pc_response = v4.getUserOfSomePeriod(params,params.pc_ID,stt,edt)

                h5_data_dic = v4.get_data_dic_templete(stt,edt)
                pc_data_dic = v4.get_data_dic_templete(stt,edt)

                if h5_response != None and h5_response.get('reports')[0].get('data').get('rows')!= None:
                    for res in h5_response.get('reports')[0].get('data').get('rows'):
                        r_value = res.get('metrics')[0].get('values')
                        c = datetime.datetime.strptime(str(res.get('dimensions')[1]),'%Y%m%d')
                        r_date=str(c.strftime('%Y-%m-%d'))#实际存在的日期
                        h5_data_dic[r_date]= int(str(r_value[0]))
                if pc_response != None and pc_response.get('reports')[0].get('data').get('rows')!= None:
                    for res in pc_response.get('reports')[0].get('data').get('rows'):
                        r_value = res.get('metrics')[0].get('values')
                        c = datetime.datetime.strptime(str(res.get('dimensions')[1]),'%Y%m%d')
                        r_date=str(c.strftime('%Y-%m-%d'))#实际存在的日期
                        pc_data_dic[r_date]= int(str(r_value[0]))
                ios_data_dic = getIOSorAndroidResultDict(stt,edt,'ios')
                android_data_dic = getIOSorAndroidResultDict(stt,edt,'android')

                date_keys=ios_data_dic.keys()
                total_data_dict=v4.get_data_dic_templete(stt,edt)

                for d in date_keys:
                    total_data_dict[d]=int(android_data_dic[d])+int(ios_data_dic[d])+int(h5_data_dic[d])+int(pc_data_dic[d])
                data_dict = total_data_dict
            elif src !=None and (src == 'h5' or src == 'pc'):
                return getWebUserCountTrend(request)
            elif src !=None and (src == 'ios'):
                ios_data_dic = getIOSorAndroidResultDict(stt,edt,'ios')
                data_dict = ios_data_dic

            elif src !=None and (src == 'android'):

                android_data_dic=v4.get_data_dic_templete(stt,edt)
                android_data_dic = getIOSorAndroidResultDict(('2016-11-02' if stt <'2016-11-02' else stt),(edt),'android')
                data_dict = android_data_dic
        else:
            return HttpResponse('funnel table name error')
        data_list = sorted(data_dict.iteritems(), key=lambda d:d[0])
        res_value=[]
        res_datetime=[]
        for i in range(len(data_list)):
            res_value.append(data_list[i][1])
            res_datetime.append(data_list[i][0])
        print res_value
        print res_datetime
        jsondata={'datetime':res_datetime,'data':res_value}
        jsondata = json.dumps(jsondata, sort_keys=True, separators=(',', ': '), default=defaultencode)  # 使用dumps方法格式化数据

        return HttpResponse(jsondata)
    else:
        print 1
        sql = 'select count(distinct `UUID`),date_format(date_sub(FROM_UNIXTIME('+funnel+'.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') d from '+funnel+\
            ' where date_format(date_sub(FROM_UNIXTIME('+funnel+'.log_time/1000),interval 7 HOUR),\'%Y-%m-%d\') between %(stt)s and %(edt)s '
        if src != None and src !='' and len(src)>0:
            sql = sql + 'and lower(src) = lower(\''+src+'\')'
        sql = sql +'group by d'
        cursor = connections['logdb_fdl'].cursor()


        cursor.execute(sql,{'stt':stt,'edt':edt})
        result = cursor.fetchall()
        cursor.close()
        for res in result:
            data_dict[str(res[1])] = res[0]
        data_list = sorted(data_dict.iteritems(), key=lambda d:d[0])
        res_value=[]
        res_datetime=[]
        for i in range(len(data_list)):
            res_value.append(data_list[i][1])
            res_datetime.append(data_list[i][0])
        print res_value
        print res_datetime
        jsondata={'datetime':res_datetime,'data':res_value}
        jsondata = json.dumps(jsondata, sort_keys=True, separators=(',', ': '), default=defaultencode)  # 使用dumps方法格式化数据

        if return_type==0:
            return HttpResponse(jsondata)
        else :
            return jsondata




# def getRegisterUserCountInPeriod(request):
#
#     src = request.GET.get('src')
#     channel = request.GET.get('channel')
#     stt = request.GET.get('stt')
#     edt = request.GET.get('edt')
#
#
#
#     sql='select count(pin) from user_info where date_format(date_sub(create_time,interval 7 HOUR),\'%Y-%m-%d\') ' \
#         'between \'2016-10-01\' and \'2016-10-30\''
#
#     cursor = connection.cursor()
#
#     cursor.execute(sql)
#     count = cursor.fetchall()
#     cursor.close()
#
#
#     jsondata = {'user_count': user_count,'today_count':todaycount[0][0]}
#
#     jsondata = json.dumps(jsondata, sort_keys=True, separators=(',', ': '), default=defaultencode)  # 使用dumps方法格式化数据
#     # print 'jsondata=',jsondata
#     return HttpResponse(jsondata)


