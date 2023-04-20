from flask import Flask
import requests
import json
import datetime
import pandas as pd

from pywebio.input import select, input, TEXT
from pywebio.output import *
from pywebio.platform.flask import webio_view

myapp = Flask(__name__)

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"


def datetime2UTC_Z(dt_dt, tz_info):
    return str(dt_dt.replace(microsecond=0).replace(tzinfo=tz_info).astimezone(tz=datetime.timezone.utc).isoformat()).replace('+00:00', 'Z')

# _functions.dtString2UTC_Z('2020-10-09 17:34:14',tz_delta)
def dtString2UTC_Z(DT_Str, tz_info):
    dt_dt = datetime.datetime.strptime(DT_Str, '%Y-%m-%d %H:%M:%S')
    return datetime2UTC_Z(dt_dt, tz_info)

# GET WEB SERVICE BY TYPE AND ID - RETURNS TYPE BY ID
def get_type_id(apitype, apiurl, apiheaders, rec_id, apiuser=None, apipass=None):
    # Limit of maxCallPerSec calls per second
    # time.sleep(1/v_sleep)

    url = apiurl + '/' + apitype 
    url = url + '/' + rec_id
    if apiuser is not None and apipass is not None:
        return requests.get(url, headers=apiheaders, auth=(apiuser, apipass))
    else: 
        return requests.get(url, headers=apiheaders)

def task_func():

    apiheaders = {
    #'Authorization': "",
    'accept-encoding': "gzip, deflate",
    'Connection': "keep-alive",
    'cache-control': "no-cache",
    'Accept': "*/*"
    }

    # storebub API
    rec_id  = ''
    apiurl  = 'https://api.storehubhq.com'
    apiuser = ''
    apipass = ''
    tz_int = 8
    outlet = ""
    apitype   = 'transactions'

    apiuser = input("What is the API Username?")
    apipass = input("What is the API Password?")

    start_date = input('Insert start date (Eg. 2019-01-09): ', type=TEXT)
    start_datetime = start_date + ' 00:00:00'

    end_date = input('Insert end date (Eg. 2019-03-05): ', type=TEXT)
    end_datetime = end_date + ' 00:00:00'

    tz_delta = datetime.timezone(datetime.timedelta(hours=tz_int))

    sinceTxt = dtString2UTC_Z(start_datetime, tz_delta) + "&to=" + dtString2UTC_Z(end_datetime, tz_delta)

    rec_id    = "?from=" + sinceTxt
    resp      = get_type_id(apitype, apiurl, apiheaders, rec_id, apiuser, apipass)

    t_data = ''

    # If get respond from API call
    if resp.status_code == 200:
        t_data = json.loads(resp.text)
        
        # saveJson = "test_load.json"
        # with open(saveJson, 'w', encoding='utf-8') as f:
        #     json.dump(t_data, f, indent=4, sort_keys=True)
       
        try:
            trans_data = pd.json_normalize(t_data)
            trans_data = trans_data[['invoiceNumber', 'total', 'isCancelled']]
            trans_data = trans_data.rename({'invoiceNumber':'Receipt No.','total':'Total Sales Amount','isCancelled':'Cancel Flag'}, axis='columns')
            trans_list = trans_data.values.tolist()

            html_str = '<h3>' + outlet + '</h3>'
            popup('Transaction Details', [
                put_html(html_str),
                'From: ' + start_date + ' Until: ' + end_date,  # equal to put_text('plain html: <br/>')
                put_table(trans_list, header=['Receipt No.', 'Total Amount', 'Cancel Flag']),
                put_buttons(['close'], onclick=lambda _: close_popup())
                ])
        except:
            html_str = '<h3>' + outlet + '</h3>'
            popup('Transaction Details',[
                put_html(html_str),
                'No transaction data from ' + start_date + ' until ' + end_date,
                put_buttons(['close'], onclick=lambda _: close_popup())
                ])
            
    else:
        print('Status code error')


myapp.add_url_rule('/', 'webio_view', webio_view(task_func),
            methods=['GET', 'POST', 'OPTIONS'])  # need GET,POST and OPTIONS methods

myapp.run(host='localhost', port=80)
