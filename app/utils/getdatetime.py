#!/usr/bin/python3
#-*- coding: utf-8 -*-

import datetime
import calendar


now_time = datetime.datetime.now()

# print('year : ' + str(time.year) + ' month : ' + str(time.month))

# 求当前月第一天
def get_first_day_of_current_month():
	first_day_of_current_month = datetime.date(now_time.year, now_time.month, 1)
	return first_day_of_current_month

# 求当前月的最后一天
def get_last_day_of_current_month():
	days_num = calendar.monthrange(get_first_day_of_current_month().year, get_first_day_of_current_month().month)[1]  # 获取当前月有多少天
	last_day_of_current_month = get_first_day_of_current_month() + datetime.timedelta(days = days_num - 1)  # 当前月的最后一天只需要days_num - 1 即可
	return last_day_of_current_month

# 求前一个月最后一天
def get_last_day_of_pre_month():
	last_day_of_pre_month = get_first_day_of_current_month() - datetime.timedelta(days = 1) # timedelta是一个不错的函数
	return last_day_of_pre_month

# 求前一个月的第一天
def get_first_day_of_pre_month():
	first_day_of_pre_month = datetime.date(get_first_day_of_pre_month().year, get_first_day_of_pre_month().month, 1)
	return first_day_of_pre_month

# 求下个月的第一天
def get_first_day_of_next_month():
	days_num = calendar.monthrange(get_first_day_of_current_month().year, get_first_day_of_current_month().month)[1]  # 获取当前月有多少天
	first_day_of_next_month = get_first_day_of_current_month() + datetime.timedelta(days = days_num)
	return first_day_of_next_month

# 求下个月的最后一天
def get_last_day_of_next_month():
	next_month_days = calendar.monthrange(get_first_day_of_next_month().year, get_first_day_of_next_month().month)[1]  # 获取下个月有多少天
	last_day_of_next_month = get_first_day_of_next_month() + datetime.timedelta(days = next_month_days - 1)
	return last_day_of_next_month


# 求当年第一天
def first_day_of_current_year():
	first_day_of_current_year = datetime.date(now_time.year, 1, 1)
	return first_day_of_current_year

# 求上一年的最后一天
def get_last_day_of_last_year():
	last_day_of_last_year = first_day_of_current_year() + datetime.timedelta(days = -1)
	return last_day_of_last_year


