# -*- coding:utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from subprocess import Popen, PIPE
from decimal import Decimal

# Create your views here.
from order.models import *
from django.db import connection
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
	return render(request,'pay_amount_ajax.html', {})


def get_pay_detail(request):

    paydetail = 'select oi.*,spu,sku,nickname,login_email from order_info oi inner join user_info ui on oi.pin=ui.pin inner join order_sub_info osi on oi.order_no=osi.order_no inner join order_sub_detail osd on osi.sub_order_no=osd.sub_order_no where oi.create_time>\'2016-07-19 00:00:00\' order by oi.create_time desc'


    cursor = connection.cursor()


    cursor.execute(paydetail)
    detail = cursor.fetchall()
    print detail

    jsondata={'detail': detail}

    # jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据
    # print jsondata
    return render(request,'pay_detail.html', jsondata)


def get_ammount_ajax(request):
	todaysql = 'select sum(pay_amount)/100 all_amount from pay_info where datediff(now(),create_time)<=1 and (status_code_s=\'completed\' or status_code_s=\'1\')'


	cursor = connection.cursor()


	cursor.execute(todaysql)
	todayamount = cursor.fetchall()



	cursor.close()
	today = datetime.date.today()
	day = []
	amount = []
        #print todayamount

	if todayamount[0][0]:
		todayamount='%.2f'%todayamount[0][0]
	else :
		todayamount='0.00'
	# print allamount
	# print todayamount

	jsondata={'today_amount': todayamount}

	jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据
	# print jsondata
	return HttpResponse(jsondata)


def get_ammount_7d_ajax(request):
	sevendaysql_gmv = 'select case when d1 is null then 0 else all_amount end ,d1,d2 from (select sum(pay_amount)/100 all_amount,datediff(now(),create_time) d1 from order_info where datediff(now(),create_time) between 0 and 7 group by datediff(now(),create_time))v right join (select 0 as d2 union all select 1 union all select 2 union all select 3 union all select 4  union all select 5  union all select 6  union all select 7 ) t on v.d1=t.d2 order by d2 desc'

	sevendaysql_count = 'select case when d1 is null then 0 else all_amount end ,d1,d2 from (select count(*) all_amount,datediff(now(),create_time) d1 from order_info where datediff(now(),create_time) between 0 and 7 group by datediff(now(),create_time))v right join (select 0 as d2 union all select 1 union all select 2 union all select 3 union all select 4  union all select 5  union all select 6  union all select 7 ) t on v.d1=t.d2 order by d2 desc'

	# res = Info.objects.raw(raw_sql)
	# for r in res:
	# 	print r.all_amount;
	# res = Info.objects.all()
	cursor = connection.cursor()

	cursor.execute(sevendaysql_gmv)
	sevendayamount = cursor.fetchall()

	cursor.execute(sevendaysql_count)
	sevendaycount = cursor.fetchall()

	# print sevendayamount
	# print sevendaycount

	cursor.close()
	day = []
	amount = []
	for r in sevendayamount:
		day.append(int(r[2]))
		amount.append('%.2f' % float(r[0]))

	day=[7,6,5,4,3,2,1,'今天']
	# print day
	# print amount

	day2 = []
	count = []
	for r in sevendaycount:
		day2.append(int(r[2]))
		count.append(int(r[0]))
	# print day
	# print count
	jsondata={'sevenday_amount':(sevendayamount),'day':(day),'amount':(amount),'sevenday_count':(sevendayamount),'day2':(day2),'count':(count)}

	jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据
	# print jsondata
	return HttpResponse(jsondata)




