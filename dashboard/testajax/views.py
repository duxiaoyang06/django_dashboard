# -*- coding:utf-8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.shortcuts import render

import json
from subprocess import Popen, PIPE


def index(request):
	'''''No comment'''
	return render(request,'index.html', {})



def json_tasklist(request):
	'''''产生Json数据并显示在页面中
	Args:
		None
	Returns:
		dict:    {"arr":array_with_tasklist}
	Raises:
		None
	'''
	# 通过Popen命令执行cmd下的tasklist命令（windows中），在linux里面对应是使用ps -ef命令
	# 下面以tasklist命令为例，如果是ps -ef命令，分隔符和行格式都要相应变化
	p = Popen(['tasklist'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
	# 转义unicode字符串并且按行分割成临时数组
	arr_temp = p.stdout.read().decode('gbk').split('\r\n')
	col_len = []  # 此数组用于记录每一个列的宽度
	total_col = len(arr_temp[2].split(" "))  # 共有多少列（实际上就是5列）
	for col in arr_temp[2].split(" "):
		col_len.append(len(col))

	arr_p = []  # 此数组存储最终的数据结果
	for line in arr_temp[2:]:
		if line != "":  # 跳过空行（首尾）
			line_col = []  # 每一行列数据的集合数组
			left = 0  # 数据片段的左端点
			right = 0  # 数据片段的右端点，结合在一起用来切分line字符串的
			for i in range(total_col):
				if i == 0:
					left = 0
				else:
					left = right + 1
				right = left + col_len[i]
				line_col.append(line[left:right])  # 切开，如果想要更完美一点，应该还需要trim一下的，不过python已经默认帮我们做了。
			arr_p.append(line_col)
	jsondict = {"arr": arr_p}  # 生成json字典，形如：{"key1":[array1],"key2":"value2",......}
	jsondata = json.dumps(jsondict)  # 使用dumps方法格式化数据
	# print jsondata
	return HttpResponse(jsondata)
