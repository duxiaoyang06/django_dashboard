# -*- coding:utf-8 -*-

"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from mysite.views import helloworld
from user import views as users_views
from order import views as order_views
from offline import views as offline_views
from spu import views as spu_views

from django.conf import settings

# from feedback import views as feedback_views
# from testajax import views as testajax_views
# from pay import views as pay_views
# from fdl import views as fdl_views
from designer import views as designer_views
from daily import views as daily_views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('^helloworld/$', helloworld),
    # url(r'^userinfo/count', users_views.get_all_users),
    # url(r'^userinfo/7d', users_views.get_user_7d),
    # url(r'^userinfo/7d_ajax', users_views.get_user_7d),
    #
    # url(r'^orderinfo/amount', order_views.get_ammount),
    # url(r'^orderinfo/7d', order_views.get_ammount_7d),
    #
    # url(r'^orderinfo/status', order_views.get_order_status),
    # url(r'^orderinfo/source', order_views.get_order_source),

    # url(r'^feedback/status', feedback_views.get_all_feedback),

    # url(r'^report', order_views.get_report),
    # url(r'^mreport', order_views.get_report_m),

    # url(r'^ranklist', fdl_views.get_ammount),

    # url(r'^mranklist', fdl_views.get_ammount_m),



    # url(r'^index', testajax_views.index),
    # url(r'^json/json_tasklist/', testajax_views.json_tasklist),

    # url(r'^orderajax7d/', order_views.index7d),
    # url(r'^ajax/order/7d', order_views.get_ammount_7d_ajax),


    ###############################################

    url(r'^userQuery/WebUserCountTrend$', users_views.getWebUserCountTrend),#正则原因 先把长的路径配在前面
    url(r'^userQuery/WebUserCount', users_views.getWebUserCount),
    url(r'^userQuery/AppUserCountTrend', users_views.getAppUserCountTrend),
    url(r'^userQuery/AppUserCount', users_views.getAppUserCount),

    #url(r'^userQuery/RegisterUserCountTrend$', users_views.getRegisterUserCount),
    url(r'^userQuery/RegisterUserCount', users_views.getRegisterUserCount),

    url(r'^offlineQuery/TotalRegisterUserCountTrend', offline_views.getTotalRegisterUserCountInPeriod),
    url(r'^offlineQuery/RegisterUserCountTrend', offline_views.getRegisterUserCountInPeriod),
    url(r'^offlineQuery/channelName', offline_views.getChannelName),

    url(r'^orderQuery/RevenuePerOrderTrend$', order_views.getRevenuePerOrderInPeriod),
    url(r'^orderQuery/RevenueTrend$', order_views.getRevenueInPeriod),
    url(r'^orderQuery/RevenuePerOrder', order_views.getRevenuePerOrder),

    url(r'^orderQuery/Revenue', order_views.getRevenue),


    #url(r'^orderQuery/PurchasedUserCountPerOrderTrend$', order_views.getPurchasedUserCountPerOrderInPeriod),
    url(r'^orderQuery/PurchasedUserCountPerOrder', order_views.getPurchasedUserCountPerOrder),

    url(r'^orderQuery/PlatformRevenue$', order_views.getRevenueByPlatform),
    url(r'^orderQuery/PaymentFailure$', order_views.getPaymentFailure),
    url(r'^orderQuery/Ouc$', order_views.getOuc),
    url(r'^orderQuery/Oic$', order_views.getOic),
    url(r'^orderQuery/Oc$', order_views.getOc),
    url(r'^orderQuery/Or$', order_views.getOr),
    url(r'^orderQuery/Oac$', order_views.getOac),
    url(r'^orderQuery/ItemDataofYesterday', order_views.getItemDataofYesterday),

    url(r'^orderQuery/TopItems$', order_views.getTopItems),
    url(r'^orderQuery/TopSale$', order_views.getTopSale),

    #url(r'^userQuery/Query', users_views.getUserQuery),
    url(r'^designerQuery/DesignerNickname', designer_views.getDesignerName),
    url(r'^spuQuery/CategoryName', spu_views.getCategoryName),

    url(r'^offlineQuery/SpuFunnel', offline_views.getSpuFunnel),
    #url(r'^offlineQuery/UserFunnel', offline_views.getUserFunnel),
    url(r'^userQuery/UserFunnelConversionDataofYesterday', users_views.getUserFunnelConversionDataofYesterday),
    url(r'^userQuery/UserFunnelTable$', users_views.getUserFunnelTable),

    url(r'^userQuery/UserFunnel$', users_views.getUserFunnel),

    url(r'^dailyQuery/dailyClick', daily_views.getTopicThroughtRate),
    url(r'^dailyQuery/dailyUV', daily_views.getDailyUVTrend),


    ###############################################

    # url(r'^orderajaxamount', order_views.index_amount),
    # url(r'^ajax/order/amount', order_views.get_ammount_ajax),
    #
    # url(r'^orderajaxstatus', order_views.index_status),
    # url(r'^ajax/order/status', order_views.get_order_status_ajax),
    #
    # url(r'^orderajaxsource', order_views.index_source),
    # url(r'^ajax/order/source', order_views.get_order_source_ajax),
    #
    # url(r'^userajax7d', users_views.index_user7d),
    # url(r'^ajax/user/7d', users_views.get_user_7d_ajax),
    #
    # url(r'^userajaxamount', users_views.index_amount),
    # url(r'^ajax/user/amount', users_views.get_all_users_ajax),
    #
    # url(r'^payajaxamount', pay_views.index_amount),
    # url(r'^ajax/pay/amount', pay_views.get_ammount_ajax),
    #
    # url(r'^designerajaxamount', designer_views.index_amount),
    # url(r'^ajax/designer/follow', designer_views.get_follow_ajax),
    #
    # url(r'^designerajaxtrend/(.+)/$', designer_views.index_trend),
    # url(r'^ajax/designer/trend/(.+)/$', designer_views.get_follow_trend),

    # url(r'^paydetail', pay_views.get_pay_detail),

    # url(r'^log/statistics', fdl_views.get_ammount),
]
