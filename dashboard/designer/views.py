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

def getDesignerName(request):
	stt = request.GET.get('stt')
	edt = request.GET.get('edt')
	src = request.GET.get('src')

	v4.getTopicClick()

	sql = 'select * from ' \
		  '(select banner_id, \'id\',erp_search_name,date_format(start_time,\'%Y-%m-%d\') tm from banner_info where banner_skip_type=3 '\
		  ' union' \
		  ' select imgtext_id, \'id\',erp_search_name,date_format(start_time,\'%Y-%m-%d\') tm from imgtext_info where imgtext_skip_type=3' \
		  ')t order by tm asc'

	cursor = connection.cursor()
	cursor.execute(sql)
	result = cursor.fetchall()
	print result
	jsondata={'pin_today': pin_today,'rate_yesterday':rate_yesterday,'rate_7daysago':rate_7daysago,'rate_30daysago':rate_30daysago}
	jsondata = json.dumps(jsondata, sort_keys=True,separators=(',', ': '),default=defaultencode)  # 使用dumps方法格式化数据

	return HttpResponse(jsondata)

