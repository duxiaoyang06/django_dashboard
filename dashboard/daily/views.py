# -*- coding:utf-8 -*-
import copy
from django.shortcuts import render
from django.http import HttpResponse
from subprocess import Popen, PIPE
from decimal import Decimal
import cPickle
# Create your views here.
from order.models import *
from django.db import connection
from django.db import connections
from ga_api import v4
from ga_api import Params
from firebase_api import bigQuery
import json
import datetime
from ga_api import v4
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
from ga_api import v4
from ga_api import Params
from firebase_api import bigQuery
import json
import datetime
from ga_api import v4
params=Params.Params()


topic_sql = ' select t.*,tci.tci_title from ' \
        ' (select banner_skip sid, \'id\',erp_search_name,date_format(date_sub(start_time,interval 7 hour),\'%Y-%m-%d\') tm from banner_info where banner_skip_type=3 '\
        ' union' \
        ' select imgtext_skip sid, \'id\',erp_search_name,date_format(date_sub(start_time,interval 7 hour),\'%Y-%m-%d\') tm from imgtext_info where imgtext_skip_type=3' \
        ')t inner join topic_content_info tci on t.sid=tci.tci_id order by tm asc'
PERIOD = 9#取10天内的数据

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

def timeFormatter(ot,otf,ntf):
    return datetime.datetime.strptime(ot,otf).strftime(ntf)

def getDailyUVTrend(src,str_min_time,str_max_time):

    data_dict=v4.get_data_dic_templete(str_min_time,str_max_time)


    if src == 'h5' or src == 'pc':
        uv_response = v4.getDailyUVInPeriod(params,(params.h5_ID if src == 'h5' else params.pc_ID),str_min_time,str_max_time)
        if uv_response != None and uv_response.get('reports')[0].get('data').get('rows')!= None:
            for res in uv_response.get('reports')[0].get('data').get('rows'):
                r_value = res.get('metrics')[0].get('values')
                c = datetime.datetime.strptime(str(res.get('dimensions')[0]),'%Y%m%d')
                r_date=str(c.strftime('%Y-%m-%d'))#实际存在的日期
                data_dict[r_date]=r_value[0]

    elif src == 'ios' or src == 'android':
        uv_response = bigQuery.daily_visit_total('ios' if src == 'ios' else 'android',datetime.datetime.strptime(str_min_time,'%Y-%m-%d').strftime('%Y%m%d'),
                                                 datetime.datetime.strptime(str_max_time,'%Y-%m-%d').strftime('%Y%m%d'))

        for i in range(len(uv_response)):
            data_dict[datetime.datetime.strptime(str(uv_response[i]['dt']),'%Y%m%d').strftime('%Y-%m-%d')] = uv_response[i]['uv']
    else:
        h5_data_dict=v4.get_data_dic_templete(str_min_time,str_max_time)
        #pc_data_dict=v4.get_data_dic_templete(str_min_time,str_max_time)
        ios_data_dict=v4.get_data_dic_templete(str_min_time,str_max_time)
        android_data_dict=v4.get_data_dic_templete(str_min_time,str_max_time)

        h5_uv_response = v4.getDailyUVInPeriod(params,(params.h5_ID if src == 'h5' else params.pc_ID),str_min_time,str_max_time)
        if h5_uv_response != None and h5_uv_response.get('reports')[0].get('data').get('rows')!= None:
            for res in h5_uv_response.get('reports')[0].get('data').get('rows'):
                r_value = res.get('metrics')[0].get('values')
                c = datetime.datetime.strptime(str(res.get('dimensions')[0]),'%Y%m%d')
                r_date=str(c.strftime('%Y-%m-%d'))#实际存在的日期
                h5_data_dict[r_date]=r_value[0]
        # pc_uv_response= v4.getDailyUVInPeriod(params,(params.h5_ID if src == 'h5' else params.pc_ID),str_min_time,str_max_time)
        # print 'pc_uv_response:', pc_uv_response
        # if pc_uv_response != None and pc_uv_response.get('reports')[0].get('data').get('rows')!= None:
        #     for res in pc_uv_response.get('reports')[0].get('data').get('rows'):
        #         r_value = res.get('metrics')[0].get('values')
        #         c = datetime.datetime.strptime(str(res.get('dimensions')[0]),'%Y%m%d')
        #         r_date=str(c.strftime('%Y-%m-%d'))#实际存在的日期
        #         pc_data_dict[r_date]=r_value[0]

        ios_uv_response = bigQuery.daily_visit_total('ios',datetime.datetime.strptime(str_min_time,'%Y-%m-%d').strftime('%Y%m%d'),
                                                 datetime.datetime.strptime(str_max_time,'%Y-%m-%d').strftime('%Y%m%d'))
        for i in range(len(ios_uv_response)):
            ios_data_dict[datetime.datetime.strptime(str(ios_uv_response[i]['dt']),'%Y%m%d').strftime('%Y-%m-%d')] = ios_uv_response[i]['uv']

        android_uv_response = bigQuery.daily_visit_total('android',datetime.datetime.strptime(str_min_time,'%Y-%m-%d').strftime('%Y%m%d'),
                                                 datetime.datetime.strptime(str_max_time,'%Y-%m-%d').strftime('%Y%m%d'))
        for i in range(len(android_uv_response)):
            android_data_dict[datetime.datetime.strptime(str(android_uv_response[i]['dt']),'%Y%m%d').strftime('%Y-%m-%d')] = android_uv_response[i]['uv']

        days = h5_data_dict.keys()

     #   print h5_data_dict,ios_data_dict,android_data_dict
        for day in days:
            data_dict[day] = int(str(h5_data_dict[day]))+ios_data_dict[day]+android_data_dict[day]#+pc_data_dict[day]
    #print 'data_dict:',data_dict
    return data_dict

def formatTopicDataWeb(period_uv,_topics,response):
    topics=copy.deepcopy(_topics)

    if response != None and response.get('reports')[0].get('data').get('rows')!= None:

            for res in response.get('reports')[0].get('data').get('rows'):
                r_value = res.get('metrics')[0].get('values')
                tci_id = str(res.get('dimensions')[0]).split('/')[2]
                c = datetime.datetime.strptime(str(res.get('dimensions')[1]),'%Y%m%d')
                r_date=str(c.strftime('%Y-%m-%d'))#实际存在的日期

                #没有cv的那天uv不会赋值,计算rate的时候统一成0
                if topics[tci_id]['cv'].has_key(r_date):
                    topics[tci_id]['cv'][r_date]=int(str(r_value[0]))
                    topics[tci_id]['uv'][r_date]=int(period_uv[r_date])
                    topics[tci_id]['rate'][r_date]=int(str(r_value[0]))*1.0/int(period_uv[r_date])

            tci_ids=topics.keys()

            for tci_id in tci_ids:
                _dict = topics[tci_id]['rate']
                days = topics[tci_id]['rate'].keys()
                days.sort()
                sort_rate={}
                for i in range(PERIOD+1):
                    sort_rate['Day'+str(i+1)] = map(_dict.get,days)[i]
                topics[tci_id]['sort_rate']=sort_rate

            for tci_id in tci_ids:
                _dict = topics[tci_id]['cv']
                days = topics[tci_id]['cv'].keys()
                days.sort()
                sort_cv={}
                for i in range(PERIOD+1):
                    sort_cv['cv_Day'+str(i+1)] = map(_dict.get,days)[i]
                topics[tci_id]['sort_cv']=sort_cv

            for tci_id in tci_ids:
                _dict = topics[tci_id]['uv']
                days = topics[tci_id]['uv'].keys()
                days.sort()
                sort_uv={}
                for i in range(PERIOD+1):
                    sort_uv['uv_Day'+str(i+1)] = map(_dict.get,days)[i]
                del topics[tci_id]['cv']
                del topics[tci_id]['uv']
                del topics[tci_id]['rate']
                topics[tci_id]['sort_uv']=sort_uv

            return topics

def formatTopicDataAPP(period_uv,_topics,cv_query_json):
    topics=copy.deepcopy(_topics)

    tci_ids = topics.keys()
    for tci_id in tci_ids:
        topics[str(tci_id)]['sort_cv']={}
        for i in range(PERIOD+1):
            topics[str(tci_id)]['sort_cv']['cv_Day'+str(i+1)]=0
            if cv_query_json.has_key(tci_id) and cv_query_json[tci_id].has_key('Day'+str(i+1)):
                topics[str(tci_id)]['sort_cv']['cv_Day'+str(i+1)]=cv_query_json[tci_id]['Day'+str(i+1)]
        days = topics[tci_id]['uv'].keys()
        for day in days:
            topics[tci_id]['uv'][day] = period_uv[day]
        _dict = topics[tci_id]['uv']
        days.sort()
        sort_uv={}
        for i in range(PERIOD+1):
            sort_uv['uv_Day'+str(i+1)] = map(_dict.get,days)[i]
        topics[tci_id]['sort_uv']=sort_uv

#            print topics
        topics[tci_id]['sort_rate']={}
        for i in range(PERIOD+1):
            topics[tci_id]['sort_rate']['Day'+str(i+1)]= 0 if topics[tci_id]['sort_uv']['uv_Day'+str(i+1)] == 0 else topics[tci_id]['sort_cv']['cv_Day'+str(i+1)]*1.0/topics[tci_id]['sort_uv']['uv_Day'+str(i+1)]
        del topics[tci_id]['cv']
        del topics[tci_id]['uv']
        del topics[tci_id]['rate']
    return topics

def calAvgTopicThroughtRate(topics):
    tci_ids = topics.keys()
    for tci_id in tci_ids:

        _1uv = topics[tci_id]['sort_uv']['uv_Day1']
        _1cv = topics[tci_id]['sort_cv']['cv_Day1']

        _3uv = topics[tci_id]['sort_uv']['uv_Day1']+topics[tci_id]['sort_uv']['uv_Day2']+topics[tci_id]['sort_uv']['uv_Day3']
        _3cv = topics[tci_id]['sort_cv']['cv_Day1']+topics[tci_id]['sort_cv']['cv_Day2']+topics[tci_id]['sort_cv']['cv_Day3']

        _7cv = topics[tci_id]['sort_cv']['cv_Day1']+topics[tci_id]['sort_cv']['cv_Day2']+topics[tci_id]['sort_cv']['cv_Day3']\
        +topics[tci_id]['sort_cv']['cv_Day4']+topics[tci_id]['sort_cv']['cv_Day5']+topics[tci_id]['sort_cv']['cv_Day6']+\
        topics[tci_id]['sort_cv']['cv_Day7']
        _7uv = topics[tci_id]['sort_uv']['uv_Day1']+topics[tci_id]['sort_uv']['uv_Day2']+topics[tci_id]['sort_uv']['uv_Day3']\
        +topics[tci_id]['sort_uv']['uv_Day4']+topics[tci_id]['sort_uv']['uv_Day5']+topics[tci_id]['sort_uv']['uv_Day6']+\
        topics[tci_id]['sort_uv']['uv_Day7']

        avg1 = 0 if _1uv==0 else _1cv*1.0/_1uv
        avg3 = 0 if _3uv==0 else _3cv*1.0/_3uv
        avg7 = 0 if _7uv==0 else _7cv*1.0/_7uv

        topics[tci_id]['avg1']=avg1
        topics[tci_id]['avg3']=avg3
        topics[tci_id]['avg7']=avg7
    return topics
def getTopicThroughtRate(request):
    #stt = request.GET.get('stt')
    #edt = request.GET.get('edt')

    src = request.GET.get('src')
    if src == None:
        src = ''
    sql = topic_sql
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
#    print result
    str_min_time = result[0][3]
    str_max_time = result[len(result)-1][3]

    max_time = datetime.datetime.strptime(str_max_time,'%Y-%m-%d')
    str_max_time = (max_time +datetime.timedelta(PERIOD)).strftime('%Y-%m-%d')

    topics={}
    for res in result:
        stt = str(res[3])
        cv = v4.get_data_dic_templete(stt,(datetime.datetime.strptime(stt,'%Y-%m-%d')+datetime.timedelta(PERIOD)).strftime('%Y-%m-%d'))
        uv = v4.get_data_dic_templete(stt,(datetime.datetime.strptime(stt,'%Y-%m-%d')+datetime.timedelta(PERIOD)).strftime('%Y-%m-%d'))
        rate = v4.get_data_dic_templete(stt,(datetime.datetime.strptime(stt,'%Y-%m-%d')+datetime.timedelta(PERIOD)).strftime('%Y-%m-%d'))
        topics[str(res[0])]={'tci_id':str(res[0]),'title':str(res[2]),'stt':str(res[3]),'cv':cv,'uv':uv,'rate':rate}

    if src == 'h5':
        h5_response = v4.getTopicClickTrend(params=params,view_id=params.h5_ID,sdate=str_min_time,edate=str_max_time,expression="^Mobile_Daily_Topic_/topic/")
     #   print h5_response
        period_uv = getDailyUVTrend(src,str_min_time,str_max_time)
        topics = formatTopicDataWeb(period_uv,topics,h5_response)

    elif src == 'pc':
        pass
#        pc_response = v4.getTopicClickTrend(params=params,view_id=params.pc_ID,sdate=str_min_time,edate=str_max_time,expression="^PC_Daily_Topic_/topic/")
 #       topics = formatTopicDataWeb(period_uv,topics,pc_response)
  #      period_uv = getDailyUVTrend(src,str_min_time,str_max_time)


    elif src == 'ios' or src =='android':

        tmp_list={}
        for res in result:
            tmp_list[res[0]]=datetime.datetime.strptime(res[3],'%Y-%m-%d').strftime('%Y%m%d')
        cv_query_json=bigQuery.daily_click_format(src,tmp_list)
        period_uv = getDailyUVTrend(src,str_min_time,str_max_time)
        topics = formatTopicDataAPP(period_uv,topics,cv_query_json)
    else:
        h5_response = v4.getTopicClickTrend(params=params,view_id=params.h5_ID,sdate=str_min_time,edate=str_max_time,expression="^Mobile_Daily_Topic_/topic/")
        h5_period_uv = getDailyUVTrend('h5',str_min_time,str_max_time)
        h5_topics = formatTopicDataWeb(h5_period_uv,topics,h5_response)
 #       pc_response = v4.getTopicClickTrend(params=params,view_id=params.pc_ID,sdate=str_min_time,edate=str_max_time,expression="^PC_Daily_Topic_/topic/")
#        pc_topics = formatTopicDataWeb(period_uv,topics,pc_response)

        tmp_list={}
        for res in result:
            tmp_list[res[0]]=datetime.datetime.strptime(res[3],'%Y-%m-%d').strftime('%Y%m%d')
        cv_query_json=bigQuery.daily_click_format('ios',tmp_list)
        ios_period_uv = getDailyUVTrend('ios',str_min_time,str_max_time)
        ios_topics = formatTopicDataAPP(ios_period_uv,topics,cv_query_json)

        tmp_list={}
        for res in result:
            tmp_list[res[0]]=datetime.datetime.strptime(res[3],'%Y-%m-%d').strftime('%Y%m%d')
        cv_query_json=bigQuery.daily_click_format('android',tmp_list)
        android_period_uv = getDailyUVTrend('android',str_min_time,str_max_time)

        android_topics = formatTopicDataAPP(android_period_uv,topics,cv_query_json)
        tci_ids = h5_topics.keys()

        total_topics={}
        for tci_id in tci_ids:
            total_topics[tci_id]={}

            #pc_topics[tci_id]
            total_topics[tci_id]['sort_cv']={}
            total_topics[tci_id]['sort_uv']={}
            total_topics[tci_id]['sort_rate']={}
            total_topics[tci_id]['stt']=ios_topics[tci_id]['stt']
            total_topics[tci_id]['title']=ios_topics[tci_id]['title']
            total_topics[tci_id]['tci_id']=ios_topics[tci_id]['tci_id']

            for i in range(PERIOD+1):
                total_topics[tci_id]['sort_cv']['cv_Day'+str(i+1)]=ios_topics[tci_id]['sort_cv']['cv_Day'+str(i+1)]\
                +android_topics[tci_id]['sort_cv']['cv_Day'+str(i+1)]\
                +h5_topics[tci_id]['sort_cv']['cv_Day'+str(i+1)]
                total_topics[tci_id]['sort_uv']['uv_Day'+str(i+1)]=ios_topics[tci_id]['sort_uv']['uv_Day'+str(i+1)]\
                +android_topics[tci_id]['sort_uv']['uv_Day'+str(i+1)]\
                +h5_topics[tci_id]['sort_uv']['uv_Day'+str(i+1)]

                total_topics[tci_id]['sort_rate']['Day'+str(i+1)]=0 if total_topics[tci_id]['sort_uv']['uv_Day'+str(i+1)]==0\
                else total_topics[tci_id]['sort_cv']['cv_Day'+str(i+1)]*1.0/total_topics[tci_id]['sort_uv']['uv_Day'+str(i+1)]
        topics = total_topics
#        print topics


#    print topics
        #v4.getTopicClickTrend(params=params,view_id=params.g_pc_ID,sdate=str_min_time,edate=str_max_time)

    topics=calAvgTopicThroughtRate(topics)

    jsondata=topics
    jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据

    return HttpResponse(jsondata)





def calWebTopicBrowse(topics,browse_response):
    if browse_response != None and browse_response.get('reports')[0].get('data').get('rows')!= None:
        for res in browse_response.get('reports')[0].get('data').get('rows'):
            r_value = res.get('metrics')[0].get('values')
            tci_id = str(res.get('dimensions')[0]).split('/')[2]
            if topics.has_key(tci_id):
                topics[tci_id]['bounceRate']= topics[tci_id]['bounceRate']+float(r_value[0])
                topics[tci_id]['duration']=topics[tci_id]['duration']+float(r_value[1])

def calWebTopicWCCP(topics,WCCP_response):
    if WCCP_response != None and WCCP_response.get('reports')[0].get('data').get('rows')!= None:
        for res in WCCP_response.get('reports')[0].get('data').get('rows'):
            r_value = res.get('metrics')[0].get('values')
            if(len(str(res.get('dimensions')[0]).split('_'))!=3):
                continue
            tci_id = str(res.get('dimensions')[0]).split('_')[2]
    #        print tci_id
            if topics.has_key(tci_id):
                topics[tci_id]['atc']= topics[tci_id]['atc']+int(r_value[0])
                topics[tci_id]['checkout']=topics[tci_id]['checkout']+int(r_value[1])
                topics[tci_id]['paid']=topics[tci_id]['paid']+int(r_value[2])


def getTopicFunnel(request):
    stt = request.GET.get('stt')
    edt = request.GET.get('edt')
    src = request.GET.get('src')
  #  print stt
   # print edt
    sql = topic_sql
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()

    topics={}
    for res in result:
        topics[str(res[0])]={'tci_id':str(res[0]),'title':str(res[2]),'stt':str(res[3]),'bounceRate':0,
                             'duration':0,'atw':0,'atc':0,'checkout':0,'paid':0}
#    print src
    if src !=None and (src == 'h5' or src == 'pc'):
        web_Browse_response = v4.getTopicBrowse(params,params.h5_ID if src == 'h5' else params.pc_ID,sdate=stt,edate=edt)
        web_WCCP_response = v4.getTopicWCCP(params,params.h5_ID if src == 'h5' else params.pc_ID,sdate=stt,edate=edt)
 #       print web_WCCP_response
        calWebTopicBrowse(topics,web_Browse_response)
        calWebTopicWCCP(topics,web_WCCP_response)
#        print topics
    jsondata=topics
    jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据

    return HttpResponse(jsondata)


#日活
#print active_user('ios',"20161012","20161012")
#print active_user('android',"20161105","20161106")


#daily_visit total
#print daily_visit_total('ios',"20161101","20161206")
#print daily_visit_total('android',"20161101","20161206")


#daily_click
#print daily_click('ios',"20161101","20161109")
#print daily_click('android',"20161101","20161109")

#tmp_list={'201':'20161105','202':'20161105'}
#print daily_click_format('ios',tmp_list)
#print daily_click_format('android',tmp_list)

def formatData(response):
    r_value = 0
    if response != None and response.get('reports')[0].get('data').get('rows')!= None:
        for res in response.get('reports')[0].get('data').get('rows'):
            r_value = res.get('metrics')[0].get('values')[0]
    return r_value



def getTopicData(request):
###############uv部分
    try:
        q = bigQuery.active_user('ios',timeFormatter(v4.strtoday,'%Y-%m-%d','%Y%m%d'),timeFormatter(v4.strtoday,'%Y-%m-%d','%Y%m%d'))
        iuv0 = 0 if len(q)==0 else q[0]['uv']
    except Exception,e:
        iuv0 = 0
    try:
        q = bigQuery.active_user('android',timeFormatter(v4.strtoday,'%Y-%m-%d','%Y%m%d'),timeFormatter(v4.strtoday,'%Y-%m-%d','%Y%m%d'))
        auv0 = 0 if len(q)==0 else q[0]['uv']
    except Exception,e:
        auv0 = 0
    huv0 = formatData(v4.getTopicClickTrend(params,params.h5_ID,v4.strtoday,v4.strtoday))
    puv0 = formatData(v4.getDailyUVInPeriod(params,params.pc_ID,v4.strtoday,v4.strtoday))
    A = int(iuv0)+int(auv0)+int(huv0)+int(puv0)

    try:
        q = bigQuery.active_user('ios',timeFormatter(v4.stryesterday,'%Y-%m-%d','%Y%m%d'),timeFormatter(v4.stryesterday,'%Y-%m-%d','%Y%m%d'))
        iuv1 = 0 if len(q)==0 else q[0]['uv']
    except Exception,e:
        iuv1 = 0
    try:
        q = bigQuery.active_user('android',timeFormatter(v4.stryesterday,'%Y-%m-%d','%Y%m%d'),timeFormatter(v4.stryesterday,'%Y-%m-%d','%Y%m%d'))
        auv1 = 0 if len(q)==0 else q[0]['uv']
    except Exception,e:
        auv1 = 0
    huv1 = formatData(v4.getDailyUVInPeriod(params,params.h5_ID,v4.stryesterday,v4.stryesterday))
    puv1 = formatData(v4.getDailyUVInPeriod(params,params.pc_ID,v4.stryesterday,v4.stryesterday))
    B = int(iuv1)+int(auv1)+int(huv1)+int(puv1)

    try:
        q = bigQuery.active_user('ios',timeFormatter(v4.str_7daysago,'%Y-%m-%d','%Y%m%d'),timeFormatter(v4.str_7daysago,'%Y-%m-%d','%Y%m%d'))
        iuv7 = 0 if len(q)==0 else q[0]['uv']
    except Exception,e:
        iuv7 = 0
    try:
        q = bigQuery.active_user('android',timeFormatter(v4.str_7daysago,'%Y-%m-%d','%Y%m%d'),timeFormatter(v4.str_7daysago,'%Y-%m-%d','%Y%m%d'))
        auv7 = 0 if len(q)==0 else q[0]['uv']
    except Exception,e:
        auv7 = 0
    huv7 = formatData(v4.getDailyUVInPeriod(params,params.h5_ID,v4.str_7daysago,v4.str_7daysago))
    puv7 = formatData(v4.getDailyUVInPeriod(params,params.pc_ID,v4.str_7daysago,v4.str_7daysago))
    C = int(iuv7)+int(auv7)+int(huv7)+int(puv7)

    try:
        q = bigQuery.active_user('ios',timeFormatter(v4.str_30daysago,'%Y-%m-%d','%Y%m%d'),timeFormatter(v4.str_30daysago,'%Y-%m-%d','%Y%m%d'))
        iuv30 = 0 if len(q)==0 else q[0]['uv']
    except Exception,e:
        iuv30 = 0
    try:
        q = bigQuery.active_user('android',timeFormatter(v4.str_30daysago,'%Y-%m-%d','%Y%m%d'),timeFormatter(v4.str_30daysago,'%Y-%m-%d','%Y%m%d'))
        auv30 = 0 if len(q)==0 else q[0]['uv']
    except Exception,e:
        auv30 = 0
    huv30 = formatData(v4.getDailyUVInPeriod(params,params.h5_ID,v4.str_30daysago,v4.str_30daysago))
    puv30 = formatData(v4.getDailyUVInPeriod(params,params.pc_ID,v4.str_30daysago,v4.str_30daysago))

    D = int(iuv30)+int(auv30)+int(huv30)+int(puv30)
############点击部分
    try:
        q = bigQuery.daily_click('ios',v4.strtoday,v4.strtoday)
        icv0 = 0 if len(q)==0 else q[0]['uv']
    except Exception,e:
        icv0 = 0
    try:
        q = bigQuery.daily_click('android',v4.strtoday,v4.strtoday)
        acv0 = 0 if len(q)==0 else q[0]['uv']
    except Exception ,e:
        acv0 = 0
    hcv0 = formatData(v4.getTopicClickTrend(params=params,view_id=params.h5_ID,sdate=v4.strtoday,edate=v4.strtoday,expression="^Mobile_Daily_Topic_/topic/"))
    pcv0 = 0

    E = int(icv0) + int(acv0) +int(hcv0) + int(pcv0)
    #pcv0 = formatCVData(v4.getTopicClickTrend(params,params.pc_ID,v4.stryesterday,v4.stryesterday))

    try:
        q = bigQuery.daily_click('ios',v4.stryesterday,v4.stryesterday)
        icv1 = 0 if len(q)==0 else q[0]['uv']
    except Exception,e:
        icv1 = 0
    try:
        q = bigQuery.daily_click('android',v4.stryesterday,v4.stryesterday)
        acv1 = 0 if len(q)==0 else q[0]['uv']
    except Exception ,e:
        acv1 = 0
    hcv1 = formatData(v4.getTopicClickTrend(params=params,view_id=params.h5_ID,sdate=v4.stryesterday,edate=v4.stryesterday,expression="^Mobile_Daily_Topic_/topic/"))
    pcv1 = 0
    F = int(icv1) + int(acv1) + int(hcv1) + int(pcv1)

    try:
        q = bigQuery.daily_click('ios',v4.str_7daysago,v4.str_7daysago)
        icv7 = 0 if len(q)==0 else q[0]['uv']
    except Exception,e:
        icv7 = 0
    try:
        q = bigQuery.daily_click('android',v4.str_7daysago,v4.str_7daysago)
        acv7 = 0 if len(q)==0 else q[0]['uv']
    except Exception ,e:
        acv7 = 0
    hcv7 = formatData(v4.getTopicClickTrend(params=params,view_id=params.h5_ID,sdate=v4.str_7daysago,edate=v4.str_7daysago,expression="^Mobile_Daily_Topic_/topic/"))
    gcv7 = 0
    G = int(icv7) + int(acv7) + int(hcv7) + int(gcv7)

    try:
        q = bigQuery.daily_click('ios',v4.str_30daysago,v4.str_30daysago)
        icv30 = 0 if len(q)==0 else q[0]['uv']
    except Exception,e:
        icv30 = 0
    try:
        q = bigQuery.daily_click('android',v4.str_30daysago,v4.str_30daysago)
        acv30 = 0 if len(q)==0 else q[0]['uv']
    except Exception ,e:
        acv30 = 0
    hcv30 = formatData(v4.getTopicClickTrend(params=params,view_id=params.h5_ID,sdate=v4.str_30daysago,edate=v4.str_30daysago,expression="^Mobile_Daily_Topic_/topic/"))
    pcv30 = 0
    H = int(icv30) + int(acv30) + int(hcv30) + int(pcv30)

    jsondata={'uv':A,'uv1':'N/A' if B==0 else A*1.0/B,'uv7':'N/A' if C==0 else A*1.0/C,'uv30':'N/A' if D==0 else A*1.0/D,
              'cv':E,'cv1':'N/A' if F==0 else E*1.0/F,'cv7':'N/A' if G==0 else E*1.0/G,'cv30':'N/A' if H==0 else E*1.0/H}
    jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据

    return HttpResponse(jsondata)

