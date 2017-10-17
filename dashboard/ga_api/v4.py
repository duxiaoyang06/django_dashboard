#-*- coding:utf-8 -*-
# """Hello Analytics Reporting API V4."""

import argparse
from oauth2client.service_account import ServiceAccountCredentials

from apiclient.discovery import build

import time,datetime
from oauth2client import client
from oauth2client import file
from oauth2client import tools
from ga_api import Params


today=datetime.date.today()+datetime.timedelta(-1)
yesterday=today+datetime.timedelta(-2)
_7daysago=today+datetime.timedelta(-8)
_30daysago=today+datetime.timedelta(-31)

strtoday=str(today)
stryesterday=str(yesterday)
str_7daysago=str(_7daysago)
str_30daysago=str(_30daysago)


#today=time.strftime("%Y-%m-%d", today)

def getUserOfSomeDay(param,view_id,sdate=str(today),edate=str(today)):

    global today
    global yesterday
    global _7daysago
    global _30daysago

    strtoday=str(today)

    stryesterday=str(yesterday)
    str_7daysago=str(_7daysago)
    str_30daysago=str(_30daysago)

    # Use the Analytics Service Object to query the Analytics Reporting API V4.
    # 今日
    res0=param.analytics.reports().batchGet(
        body={
                'reportRequests': [
                {
                    'viewId': view_id,
                    'dateRanges': [{'startDate': strtoday, 'endDate': strtoday}],
                    'metrics': [{'expression': 'ga:1dayUsers'}],
                    'dimensions':[{'name':'ga:date'}]
                }
                ]
            }
    ).execute()

    # 昨日
    res1=param.analytics.reports().batchGet(
        body={
                'reportRequests': [
                {
                    'viewId': view_id,
                    'dateRanges': [{'startDate': stryesterday, 'endDate': stryesterday}],
                    'metrics': [{'expression': 'ga:1dayUsers'}],
                    'dimensions':[{'name':'ga:date'}]
                }
                ]
            }
    ).execute()

    # 7日之前的今天
    res2=param.analytics.reports().batchGet(
        body={
                'reportRequests': [
                {
                    'viewId': view_id,
                    'dateRanges': [{'startDate': str_7daysago, 'endDate': str_7daysago}],
                    'metrics': [{'expression': 'ga:1dayUsers'}],
                    'dimensions':[{'name':'ga:date'}]
                }
                ]
            }
    ).execute()

    # 30日之前的今天
    res3=param.analytics.reports().batchGet(
        body={
                'reportRequests': [
                {
                    'viewId': view_id,
                    'dateRanges': [{'startDate': str_30daysago, 'endDate': str_30daysago}],
                    'metrics': [{'expression': 'ga:1dayUsers'}],
                    'dimensions':[{'name':'ga:date'}]

                }
                ]
            }
    ).execute()
    return [res0,res1,res2,res3]


def getUserOfSomePeriod(params,view_id,sdate=str(str_7daysago),edate=str(strtoday),filter=None):

    # 默认7日内

    # if filter != None:
    #     print filter
    #     print type(body['reportRequests'][0]['dimensions'])
    body={
            'reportRequests': [
            {
                'viewId': view_id,
                'dateRanges': [{'startDate': sdate, 'endDate': edate}],
                'metrics': [{'expression': 'ga:users'}],
                'dimensions':[{'name':'ga:date'}],
                # "dimensionFilterClauses": [{
                #     "filters": [{
                #     "dimension_name": "ga:landingPagePath",
                #     "operator": "exact",
                #     "expressions": ["/rae"]
                #     }]
                # }]
            }
            ]
        }
    dimensionFilterClauses=[{
                    "filters": [{
                    "dimension_name": "ga:landingPagePath",
                    "operator": "exact",
                    "expressions": [filter]
                    }]
                }]
    if filter != None:
        body['reportRequests'][0]['dimensions']=[{'name':'ga:landingPagePath'},{'name':'ga:date'}]
        body['reportRequests'][0]['dimensionFilterClauses']=dimensionFilterClauses



    return params.analytics.reports().batchGet(
        body=body
    ).execute()


def getWebUserCount(params):

    h5_response = getUserOfSomeDay(params,params.h5_ID)
    pc_response = getUserOfSomeDay(params,params.pc_ID)
    print h5_response
    h5_count=[]
    pc_count=[]

    for res in h5_response:
        try:
            h5_count.append(int( res.get('reports')[0].get('data').get('rows')[0].get('metrics')[0].get('values')[0]))
        except Exception ,e:
            h5_count.append(0)
    for res in pc_response:
        try:
            pc_count.append(int(res.get('reports')[0].get('data').get('rows')[0].get('metrics')[0].get('values')[0]))
        except Exception ,e:
            pc_count.append(0)

    print h5_count
    print pc_count

    count_today=int(h5_count[0]+pc_count[0])

    count_yesterday=int(h5_count[1]+pc_count[1])
    count_7daysago=int(h5_count[2]+pc_count[2])
    count_30daysago=int(h5_count[3]+pc_count[3])
    return {'count_today':count_today,'count_yesterday':count_yesterday,'count_7daysago':count_7daysago,'count_30daysago':count_30daysago}


def getTopicBrowse(params,view_id,sdate=str(str_7daysago),edate=str(strtoday)):
        body={
            'reportRequests': [
            {
                'viewId': view_id,
                'dateRanges': [{'startDate': sdate, 'endDate': edate}],
                'metrics': [{'expression': 'ga:bounceRate'},{'expression': 'ga:avgTimeOnPage'}],
                'dimensions':[{'name':'ga:pagePath'}],
                "dimensionFilterClauses": [{
                    "filters": [{
                    "dimension_name": "ga:pagePath",
                    #"operator": "exact",
                    "expressions": ['^/topic/\d+$']
                    }]
                }]
            }
            ]
        }

        return params.analytics.reports().batchGet(
            body=body
        ).execute()

#wishlist cart checkout paid
def getTopicWCCP(params,view_id,sdate=str(str_7daysago),edate=str(strtoday)):
        body={
            'reportRequests': [
            {
                'viewId': view_id,
                'dateRanges': [{'startDate': sdate, 'endDate': edate}],
                'metrics': [{'expression': 'ga:quantityAddedToCart'},
                            {'expression': 'ga:quantityCheckedOut'},
                            {'expression': 'ga:quantityRefunded'}],
                'dimensions':[{'name':'ga:productListName'}],
                "dimensionFilterClauses": [{
                    "filters": [{
                    "dimension_name": "ga:productListName",
                    #"operator": "exact",
                    "expressions": ['^topic.*\d+$']
                    }]
                }]
            }
            ]
        }

        return params.analytics.reports().batchGet(
            body=body
        ).execute()

def getDailyUVInPeriod(params,view_id,sdate=str(str_7daysago),edate=str(strtoday)):
        body={
            'reportRequests': [
            {
                'viewId': view_id,
                'dateRanges': [{'startDate': sdate, 'endDate': edate}],
                'metrics': [{'expression': 'ga:users'}],
                'dimensions':[{'name':'ga:date'}],
                "dimensionFilterClauses": [{
                    "filters": [{
                    "dimension_name": "ga:pagePath",
                    "operator": "exact",
                    "expressions": ['/daily']
                    },
                    {
                    "dimension_name": "ga:pagePath",
                    "operator": "exact",
                    "expressions": ['/']
                    }
                    ]
                }]
            }
            ]
        }

        return params.analytics.reports().batchGet(
            body=body
        ).execute()

def getTopicCV(params,view_id,sdate=str(str_7daysago),edate=str(strtoday),expression=""):
        body={
            'reportRequests': [
            {
                'viewId': view_id,
                'dateRanges': [{'startDate': sdate, 'endDate': edate}],
                'metrics': [{'expression': 'ga:users'}],
                'dimensions':[{'name':'ga:date'}],
                "dimensionFilterClauses": [{
                    "filters": [{
                    "dimension_name": "ga:eventCategory",
               #     "operator": "exact",
                    "expressions": [expression]
                    }]
                }]
            }
            ]
        }
        return params.analytics.reports().batchGet(
            body=body
        ).execute()


def getTopicClickTrend(params,view_id,sdate=str(str_7daysago),edate=str(strtoday),expression=""):
        body={
            'reportRequests': [
            {
                'viewId': view_id,
                'dateRanges': [{'startDate': sdate, 'endDate': edate}],
                'metrics': [{'expression': 'ga:users'}],
                'dimensions':[{'name':'ga:eventCategory'},{'name':'ga:date'}],
                "dimensionFilterClauses": [{
                    "filters": [{
                    "dimension_name": "ga:eventCategory",
                  #  "operator": "exact",
                    "expressions": [expression]
                    }]
                }]
            }
            ]
        }
        # dimensionFilterClauses=[{
        #             "filters": [{
        #             "dimension_name": "ga:landingPagePath",
        #             "operator": "exact",
        #             "expressions": [filter]
        #             }]
        #         }]
        # if filter != None:
        #     body['reportRequests'][0]['dimensions']=[{'name':'ga:landingPagePath'},{'name':'ga:date'}]
        #     body['reportRequests'][0]['dimensionFilterClauses']=dimensionFilterClauses
        #
        #

        return params.analytics.reports().batchGet(
            body=body
        ).execute()


# def getDailyData(params,view_id,sdate=str(str_7daysago),edate=str(strtoday)):
#         body={
#             'reportRequests': [
#                     {
#                 'viewId': view_id,
#                 'dateRanges': [{'startDate': sdate, 'endDate': edate}],
#                 'metrics': [{'expression': 'ga:users'},{'expression': 'ga:pageViews'}],
#                 #'dimensions':[{'name':'ga:eventCategory'},{'name':'ga:date'}],
#                 "dimensionFilterClauses": [{
#                     "filters": [{
#                     "dimension_name": "ga:pagePath",
#                     "operator": "exact",
#                     "expressions": ['/daily']
#                     },
#                     ]
#                 },
#                 {
#                     "filters": [{
#                     "dimension_name": "ga:pagePath",
#                     "operator": "exact",
#                     "expressions": ['/']
#                     },
#                     ]
#                 }
#                 ]
#             }
#             ]
#         }
#         return params.analytics.reports().batchGet(
#             body=body
#         ).execute()

#获得一个数据结构为{'2016-10-10':0}样式的字典,范围是开始结束时间,每天初始化为0
def get_data_dic_templete(sdata,edate):
    data_dic={}
    s_tmp=sdata
    while True:
        data_dic[str(s_tmp)] = 0
        if s_tmp == edate:
            break
        _tmp = datetime.datetime.strptime(s_tmp,'%Y-%m-%d')+datetime.timedelta(1)
        _tmp.strftime('%Y-%m-%d')
        s_tmp=_tmp.strftime('%Y-%m-%d')

    return data_dic

if __name__ == '__main__':

    params=Params.Params()
    #getWebUserCount(analytics)

    data_dic=get_data_dic_templete(str_30daysago,strtoday)

    h5_response = getUserOfSomePeriod(params,params.h5_ID,'2016-10-01','2016-10-30',"/rae")
    print h5_response
    for res in h5_response.get('reports')[0].get('data').get('rows'):

        r_value = res.get('metrics')[0].get('values')
        c = datetime.datetime.strptime(str(res.get('dimensions')[1]),'%Y%m%d')

        r_date=str(c.strftime('%Y-%m-%d'))#实际存在的日期

        data_dic[r_date]= int(str(r_value[0]))

    print data_dic.keys()
    print data_dic.values()