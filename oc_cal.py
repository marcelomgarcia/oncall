#!/usr/bin/env python3
# Create a year HTML calendar.

import sys
import calendar
import bs4
import datetime

def get_year(cal):
    """Return the year of the calendar"""
    tag = cal.find('th')

    if tag['class'][0] == "year":
        return tag.string
    else:
        return ""

def get_month_name(my_date):
    pass

def find_cal_date(cal, my_date):
    """Return the day of week of 'my_date'"""
    my_dt_date = datetime.datetime.strptime(my_date, "%Y-%m-%d").date()
    # Return the name of the month: April, May, June... so we can search on the calendar.
    my_month_name = calendar.month_name[my_dt_date.month]

