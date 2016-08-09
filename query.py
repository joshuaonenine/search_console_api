#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
import csv
import cgi, cgitb
import math
import time
import threading
import signal
from googleapiclient import sample_tools
from datetime import datetime
from datetime import timedelta

def __get_country_dict():
  return {"jpn":"日本", "gbr":"イギリス", "cxx":"不明な地域", "usa":"アメリカ合衆国", "chn":"中国", "vnm":"ベトナム", "hkg":"香港", "twn":"台湾", "sgp":"シンガポール", "ind":"インド", "tha":"タイ", "aus":"オーストラリア", 
"bra":"ブラジル", "kor":"大韓民国", "svk":"スロバキア", "idn":"インドネシア", "ita":"イタリア", "can":"カナダ", "deu":"ドイツ", "mys":"マレーシア", "fra":"フランス", "tur":"トルコ", "phl":"フィリピン:", "nga":"ナイジェリア", "irl":"アイルランド", "irn":"イラン", "gum":"グアム", "sau":"サウジアラビア", "rus":"ロシア", "arg":"アルゼンチン", "mmr":"ミャンマー", "rou":"ルーマニア", "mex":"メキシコ", "bel":"ベルギー", "che":"スイス", "esp":"スペイ>ン", "nld":"オランダ", "nzl":"ニュージーランド", "cze":"チェコ共和国", "aut":"オーストリア", "are":"アラブ首長国連邦", "mng":"モンゴル", "khm":"カンボジア", "zaf":"南アフリカ"}

def __get_request(form):
  dimensions = []
  filters = []

  if 'page' in form:
    dimensions.append("page")
    if 'page_expression' in form: filters.append({'dimension':'page', 'operator': form['page_operator'].value, 'expression': form['page_expression'].value})
  if 'query' in form:
    dimensions.append("query")
    if 'query_expression' in form: filters.append({'dimension':'query', 'operator': form['query_operator'].value, 'expression': form['query_expression'].value})
  if not dimensions: dimensions.append("query")

  if 'country' in form and form['country'].value != '0':
    filters.append({'dimension':'country', 'expression': form['country'].value})

  if 'device' in form and form['device'].value != '0':
    filters.append({'dimension':'device', 'expression': form['device'].value})
  search_type = form['search_type'].value if 'search_type' in form and form['search_type'].value != '0' else 'web'

  row_limit = int(form['row_limit'].value) if 'row_limit' in form and form['row_limit'].value.isdigit() else 999
  row_limit = math.floor(row_limit)
  if row_limit > 5000: row_limit = 5000

  if 'duration' in form and form['duration'].value == '2':
    request_list = []
    startdate_time = datetime.strptime(form['start_date'].value, '%Y-%m-%d')
    startdate = startdate_time.date()

    enddate_time = datetime.strptime(form['end_date'].value, '%Y-%m-%d')
    enddate = enddate_time.date()
    duration = (enddate - startdate).days

    a = 0
    while a < duration + 1:
      date = startdate + timedelta(a)
      converted_date = date.strftime('%Y-%m-%d')
      request = {
          'startDate': converted_date,
          'endDate': converted_date,
          'dimensions': dimensions,
          'dimensionFilterGroups': [{
            'filters': filters
          }],
          'searchType': search_type,
          'rowLimit': row_limit,
      }
      request_list.append(request)
      a += 1
    return request_list
  else:
    return {
    'startDate': form['start_date'].value,
    'endDate': form['end_date'].value,
    'dimensions': dimensions,
    'dimensionFilterGroups': [{
      'filters': filters
    }],
    'searchType': search_type,
    'rowLimit': row_limit
    }

def main(argv):
  cgitb.enable() 
  print('Content-type: text/html;\r\n')
  form = cgi.FieldStorage()
  service, flags = sample_tools.init(
      argv, 'webmasters', 'v3', __doc__, __file__, parents=[],
      scope='https://www.googleapis.com/auth/webmasters.readonly')
  print_row_array = []
  row2 = []
  request = __get_request(form)
  threads = []
  if isinstance(form['property_uri[]'], list):
    property_uri_list = form['property_uri[]']
    for uri in property_uri_list:
      if isinstance(request, list):
        for requestdata in request:
          thread(threads, service, uri.value, requestdata, form, print_row_array)
      else:
        thread(threads, service, uri.value, request, form, print_row_array)
  else:
    if isinstance(request, list):
      for requestdata in request:
        thread(threads, service, form['property_uri[]'].value, requestdata, form, print_row_array)
    else:
      thread(threads, service, form['property_uri[]'].value, request, form, print_row_array)
  write_rows(print_row_array)
  print("done")

def thread(threads, service, uri, requestdata, form, print_row_array):
  t = threading.Thread(target=startquery(service, uri, requestdata, form, print_row_array))
  threads.append(t)
  t.start()

def startquery(service, uri, requestdata, form, print_row_array):
  response = execute_request(service, uri, requestdata)
  time.sleep(2)
  row2 = print_table(response, uri, form, requestdata)
  print_row_array.append(row2)
  return print_row_array

def execute_request(service, property_uri, request):
  return service.searchanalytics().query(
      siteUrl=property_uri, body=request).execute()

def print_table(response, property_uri, form, requestdata):
  if 'rows' not in response: return

  rows = response['rows']
  print_row_array = []
  row2 = []

  country_str = form['country'].value if form['country'] and form['country'].value != '0' else '-'
  device = form['device'].value if form['device'] and form['device'].value != '0' else '-'
  search_type = form['search_type'].value if form['search_type'] and form['search_type'].value != '0' else '-'
  date = 'Daily' if form['duration'].value == '2' else 'Range'

  for row in rows:
    query_csv_array = []
    page_csv_array = []
    if 'keys' in row:
      key_array = row['keys']
      for key in key_array:
        csv_queries = ''
        csv_pages = ''
        key_string_csv =  key
        page_csv_array.append(key_string_csv) if key.startswith('http') else query_csv_array.append(key_string_csv)
      csv_queries = ','.join((query_csv_array))
      csv_pages = ','.join(page_csv_array)
    clicks = int(row['clicks'])
    impressions = int(row['impressions']) if 'impressions' in form else ''
    ctr = str(round(row['ctr'] * 100, 2)) + '%' if 'ctr' in form else ''
    position = round(row['position'], 2) if 'position' in form else ''
    country_dict = __get_country_dict()
    country = country_dict.get(country_str, '-')

    row2.append([property_uri, date, requestdata['startDate'], requestdata['endDate'], country, device,
    search_type, csv_queries, csv_pages, str(clicks), str(impressions), ctr, str(position)])
  return row2

def write_rows(rows):
  f = open('sample_search_console.csv', 'w', encoding='utf-8')
  writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
  writer.writerow(["Property", "Date", "Date_start", "Date_end", "Country", "Device", "SearchType", "Query", "Page",
  "Clicks", "Impressions", "CTR", "Ranking"])

  for row in rows:
    writer.writerows(row)
  f.close()

if __name__ == '__main__':
  main(sys.argv)