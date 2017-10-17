# __author__ = 'kangd'
# -*- coding: UTF-8 -*-

from google.cloud import bigquery
from oauth2client.service_account import ServiceAccountCredentials
import httplib2,re,datetime

SCOPE = ['https://www.googleapis.com/auth/bigquery.readonly']

def _get_android_client(key_file_path=None):
    SERVICE_ACCOUNT_EMAIL = 'bigquery-api@memotif-f38de.iam.gserviceaccount.com'
    if key_file_path:
        KEY_FILE_LOCATION = key_file_path
    else:
        KEY_FILE_LOCATION = '/Users/duxiaoyang/Desktop/dashboard/firebase_api/motif-android-old-254ff79ce16d.p12'

    project_id = 'memotif-f38de'
    credentials = ServiceAccountCredentials.from_p12_keyfile(
        SERVICE_ACCOUNT_EMAIL, KEY_FILE_LOCATION, scopes=SCOPE)
    http = credentials.authorize(httplib2.Http())
    client = bigquery.Client(project=project_id, http=http)
    return client

def _get_ios_client(key_file_path=None):
    SERVICE_ACCOUNT_EMAIL = 'bigquery-api@motif-2e36f.iam.gserviceaccount.com'
    if key_file_path:
        KEY_FILE_LOCATION = key_file_path
    else:
        KEY_FILE_LOCATION = '/Users/duxiaoyang/Desktop/dashboard/firebase_api/motif-ios-0f9df89efae5.p12'

    project_id = 'motif-2e36f'
    credentials = ServiceAccountCredentials.from_p12_keyfile(
        SERVICE_ACCOUNT_EMAIL, KEY_FILE_LOCATION, scopes=SCOPE)
    http  = credentials.authorize(httplib2.Http())
    client = bigquery.Client(project=project_id,http=http)
    return client

#Query
def sync_query(terminal,query,use_legacy_sql = False):

    if 'ios' == terminal.lower():
        client =  _get_ios_client()
        # query = re.sub('from\s+', 'from  me_motif_motif_IOS.', query,flags=re.I)
        query = re.sub('app_events_', 'me_motif_motif_IOS.app_events_', query, flags=re.I)
    elif 'android' == terminal.lower():
        client = _get_android_client()
        # query = re.sub('from\s+', 'from  me_motif_motif_ANDROID.', query,flags=re.I)
        query = re.sub('app_events_', 'me_motif_motif_ANDROID.app_events_', query, flags=re.I)

    # query = re.sub('app_events_'+ (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y%m%d'), 'app_events_intraday_'+ (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y%m%d'), query, flags=re.I)
    query = re.sub('app_events_'+ (datetime.date.today() - datetime.timedelta(days=0)).strftime('%Y%m%d'), 'app_events_intraday_'+ (datetime.date.today() - datetime.timedelta(days=0)).strftime('%Y%m%d'), query, flags=re.I)
    # Construct the service object for interacting with the BigQuery API.
    #print query
    query_results = client.run_sync_query(query)
    # Use standard SQL syntax for queries.
    # See: https://cloud.google.com/bigquery/sql-reference/
    query_results.use_legacy_sql = use_legacy_sql

    query_results.run()

    # Drain the query results by requesting a page at a time.
    page_token = None

    query_results_list = []
    while True:
        rows, total_rows, page_token = query_results.fetch_data(
            max_results=20,
            page_token=page_token)

        for row in rows:
            query_results_list.append(row)
            #print(row)

        if not page_token:
            break

    return query_results_list

def _get_terminal_min_date(terminal=None,start_date = None):
    android_start_date="20161102"
    ios_start_date = "20160831"
    if terminal:
        if 'ios' == terminal.lower():
            if start_date:
                return max(ios_start_date,start_date)
            else:
                return ios_start_date
        elif 'android' == terminal.lower():
            if start_date:
                return  max(android_start_date,start_date)
            else:
                return android_start_date
    else:
        return android_start_date

def _get_terminal_max_date(end_date = None):
    if end_date:
        return min(datetime.date.today().strftime('%Y%m%d'),end_date)
    else:
        return datetime.date.today().strftime('%Y%m%d')

#日活
def active_user(terminal,start_date=None,end_date=None):
    sql_template = u"(SELECT '{date}' dt,count(distinct user_dim.app_info.app_instance_id) uv from  app_events_{date} where event_dim.name = 'user_engagement'and event_dim.params.key='firebase_event_origin')"
    i = datetime.timedelta(days=0)
    tmp_list = ()
    date1=datetime.datetime.strptime(_get_terminal_min_date(terminal,start_date),'%Y%m%d')
    date2=datetime.datetime.strptime(_get_terminal_max_date(end_date),'%Y%m%d')
    while i <= (date2 - date1):
        tmp_list = tmp_list + (sql_template.format(date=(date1 + i).strftime('%Y%m%d')),)
        i += datetime.timedelta(days=1)

    sql = "select * from " + " , ".join(tmp_list) + " order by dt"
    return sync_query(terminal, sql, True)

#daily_visit total
def daily_visit_total(terminal,start_date=None,end_date=None):
    sql_template = u"(SELECT '{date}' dt,count(distinct user_dim.app_info.app_instance_id) uv from  app_events_{date} where event_dim.name = 'main_daily_item_show'and event_dim.params.key='firebase_event_origin')"
    i = datetime.timedelta(days=0)
    tmp_list = ()
    date1=datetime.datetime.strptime(_get_terminal_min_date(terminal,start_date),'%Y%m%d')
    date2=datetime.datetime.strptime(_get_terminal_max_date(end_date),'%Y%m%d')
    while i <= (date2 - date1):
        tmp_list = tmp_list + (sql_template.format(date=(date1 + i).strftime('%Y%m%d')),)
        i += datetime.timedelta(days=1)

    sql = "select * from " + " , ".join(tmp_list) + " order by dt"
    return sync_query(terminal, sql, True)


#daily_click total
def daily_click(terminal,start_date=None,end_date=None):
    sql_template = u" SELECT '{date}' dt,user_dim.app_info.app_instance_id ,event_dim_array.name,event_dim_array.params,event_dim_array.timestamp_micros " \
                   " from  app_events_{date}, UNNEST(event_dim) as event_dim_array " \
                   " where event_dim_array.name = 'main_daily_item_show' "
    i = datetime.timedelta(days=0)
    tmp_list = ()
    date1=datetime.datetime.strptime(_get_terminal_min_date(terminal,start_date),'%Y%m%d')
    date2=datetime.datetime.strptime(_get_terminal_max_date(end_date),'%Y%m%d')
    while i <= (date2 - date1):
        tmp_list = tmp_list + (sql_template.format(date=(date1 + i).strftime('%Y%m%d')),)
        i += datetime.timedelta(days=1)

    sql = "with t1 as ( " + " union all ".join(tmp_list) +" ),t2 as ( "\
          " select t1.*,tt1.key tt1_key,tt1.value.string_value tt1_value,tt2.key tt2_key,tt2.value.string_value tt2_value from " \
          " t1 join UNNEST(params) as tt1 join UNNEST(params) as tt2 " \
          " where tt1.key='daily_type' and tt2.key='daily_id') " \
          " select dt,tt2_value daily_id,count(distinct app_instance_id) uv " \
          " from t2  where tt1_value = '3' group by dt,tt2_value  order by dt asc,uv desc"
    return sync_query(terminal, sql, False)

def daily_click_format(terminal,topic_list):
    daily_click_format = {}
    min_date=None
    for (k,v) in topic_list.items():
        if min_date:
            if min_date > v:
                min_date  = v
        else:
            min_date = v

    if min_date:
        daily_click_result = daily_click(terminal, min_date,
                    datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=1), '%Y%m%d'))
        for item in daily_click_result:
            max_dt_diff = 10
            if item.get('daily_id') and topic_list.get(item.get('daily_id')) and item.get('dt') and item.get('uv'):
                dt_diff = (datetime.datetime.strptime(item.get('dt'),'%Y%m%d') - datetime.datetime.strptime(topic_list.get(item.get('daily_id')),'%Y%m%d')).days
                if max_dt_diff >= dt_diff:
                    if daily_click_format.get(item.get('daily_id')):
                        tmp_daily_id_dict = daily_click_format.get(item.get('daily_id'))
                        tmp_daily_id_dict['Day'+str(dt_diff+1)] = item.get('uv')
                        daily_click_format[item['daily_id']] = tmp_daily_id_dict
                    else:
                        tmp_daily_id_dict={}
                        tmp_daily_id_dict['Day' + str(dt_diff+1)] = item.get('uv')
                        daily_click_format[item['daily_id']] = tmp_daily_id_dict

    return daily_click_format


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