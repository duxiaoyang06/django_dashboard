from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Info(models.Model):
	order_id = models.IntegerField(primary_key=True)
	create_time = models.CharField(max_length=255)
	#update_time = models.DateTimeField
	pay_amount = models.IntegerField()
	source =  models.CharField(max_length=255)


class Sub_info(models.Model):
	sub_order_id = models.IntegerField(primary_key=True)
	status_code = models.IntegerField()