__author__ = 'wangchao'

import sys, os, re, math, random

import datetime
from dateutil.relativedelta import relativedelta

from wc_common import *

from collections import defaultdict, namedtuple

UserDayItem = namedtuple('UserDayItem', ["user_id", "report_date", "tBalance", "yBalance", "total_purchase_amt", "direct_purchase_amt", "purchase_bal_amt", "purchase_bank_amt", "total_redeem_amt", "consume_amt", "transfer_amt", "tftobal_amt", "tftocard_amt", "share_amt", "category1", "category2", "category3", "category4"])
TaobaoDayItem = namedtuple('TaobaoDayItem', ["mfd_date", "mfd_daily_yield", "mfd_7daily_yield"])
BankDayItem = namedtuple('BankDayItem', ["mfd_date", "Interest_O_N", "Interest_1_W", "Interest_2_W", "Interest_1_M", "Interest_3_M", "Interest_6_M", "Interest_9_M", "Interest_1_Y"])
UserProfileItem = namedtuple('UserProfileItem', ["user_id", "sex", "city", "constellation"])

def load_items(file_name, class_name):
    print "load " + str(file_name)
    ret = []
    in_file = open(file_name)
    in_file.readline()
    line_list = in_file.readlines()
    in_file.close()
    m = getattr(sys.modules[__name__], class_name)
    for line in line_list:
        arr = line.strip().split(",")
        item = m._make(arr)
        ret.append(item)
    return ret

def load_map_items(item_list):
    ret = {}
    for item in item_list:
        key = item[0]
        ret[key] = item
    return ret

def save_csv_file(data_list, name_list, file_name):
    out_file = open(file_name, "w")
    if name_list:
        out_file.write(arr_string(name_list, ",") + "\n")
    for data in data_list:
        out_file.write(arr_string(data, ",") + "\n")
    out_file.close()

def add_day(day_string, day_num=1):
    dt = datetime.datetime.strptime(day_string, "%Y%m%d")
    dt2 = dt + datetime.timedelta(days=day_num)
    ret_string = dt2.strftime("%Y%m%d")
    return ret_string

def build_time_map(begin_date, end_date, list_num):
    ret = {}
    date_str = begin_date
    while date_str != end_date:
        ret[date_str] = [0 for i in xrange(list_num)]
        date_str = add_day(date_str)
    return ret

def build_purchase_redeem_map(begin_date, end_date, item_list):
    m = build_time_map(begin_date, end_date, 3)
    #for k in m.keys():
    #    m[k][0] = get_week(k)
    for uitem in item_list:
        p = int(uitem.total_purchase_amt)
        r = int(uitem.total_redeem_amt)
        day_str = uitem.report_date
        if m.has_key(day_str):
            m[day_str][0] += p
            m[day_str][1] += r
    return m

def get_week(date_str):
    dt = datetime.datetime.strptime(date_str, "%Y%m%d")
    week_info = dt.isocalendar()[2]
    return week_info

def save_map(m, name_list, file_name):
    sorted_key_list = sorted(m.keys(), key= lambda x: x, reverse=False)
    l = []
    for k in sorted_key_list:
        tmp = [k]
        for v in m[k]:
            tmp.append(v)
        l.append(tmp)
    save_csv_file(l, name_list, file_name)

def add_month(day_string, month_num=1):
    dt = datetime.datetime.strptime(day_string, "%Y%m%d")
    dt2 = dt + relativedelta(months=month_num)
    ret_string = dt2.strftime("%Y%m%d")
    return ret_string

def result_arr(title, lists):
    ret = ""
    sum_score = 0.0
    for i in range(0, len(lists)):
        sum_score += lists[i][-1]
        ret += arr_string(lists[i]) + "\n"
    return title + "\t" + str(sum_score) + "\n" + ret

def plural_to_real(plu):
	return (plu.real**2 + plu.imag**2)**0.5