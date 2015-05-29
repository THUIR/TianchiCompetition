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

def load_map_list(file_name):
    print "load " + str(file_name)
    ret = {}
    in_file = open(file_name)
    in_file.readline()
    line_list = in_file.readlines()
    in_file.close()
    for line in line_list:
        arr = line.strip().split(",")
        l = []
        for i in range(1, len(arr)):
            l.append(float(arr[i]))
        ret[arr[0]] = l
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
    m = build_time_map(begin_date, end_date, 2)
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

def build_purchase_redeem_map_wrong(begin_date, end_date, item_list, taobao_day_map):
    m = build_time_map(begin_date, end_date, 3)
    #for k in m.keys():
    #    m[k][0] = get_week(k)
    fake_last_user = UserDayItem(-1, "20000101","0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0")
    item_list.append(fake_last_user)
    last_user = -2
    u_list = []
    for uitem in item_list:
        if uitem.user_id != last_user:
            s_list = sorted(u_list, key=lambda x: int(x.report_date), reverse= False)
            for i in range(0, len(s_list)):
                today_purchase = int(s_list[i].total_purchase_amt)
                today_redeem = int(s_list[i].total_redeem_amt)
                today_str = uitem.report_date
                if m.has_key(today_str):
                    m[today_str][0] += today_purchase
                    m[today_str][1] += today_redeem
                if i > 0:
                    day_count = 0
                    day_interest = []
                    last_day_str = add_day(s_list[i - 1].report_date)
                    begin_money = s_list[i - 1].tBalance
                    end_money = s_list[i].yBalance
                    tmp_str = last_day_str
                    while tmp_str != today_str:
                        tmp_str = add_day(tmp_str)
                        day_interest.append(int(float(get_map_feature_latest(taobao_day_map, tmp_str)[1]) * begin_money))
                        day_count += 1
                    if day_count > 0:
                        total_interest = sum(day_interest)
                        total_redeem_cost = max(0, begin_money + total_interest - end_money)
                        avg_redeem = int(total_redeem_cost / day_count)
                        for j in range(0, day_count):
                            target_str = add_day(last_day_str, j)
                            if m.has_key(target_str):
                                m[target_str][0] += day_interest[j]
                                m[target_str][1] += avg_redeem
            u_list = []
        u_list.append(uitem)
    return m

def get_week(date_str):
    dt = datetime.datetime.strptime(date_str, "%Y%m%d")
    week_info = dt.isocalendar()[2]
    return week_info

def get_month_day(date_str):
    dt = datetime.datetime.strptime(date_str, "%Y%m%d")
    return dt.day

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


def get_map_feature_latest(m, date_str):
        count = 0
        sub_str = date_str
        while True:
            if m.has_key(sub_str):
                return m[sub_str]
            sub_str = add_day(sub_str, -1)
            count += 1
            if count > 10:
                break
        return None


def math_log(x):
        return math.log10(1.0 + x)


def math_exp(x):
        return (10.0 ** x) - 1.0


def safe_float(x):
    if x == "":
        x = "0"
    return float(x)