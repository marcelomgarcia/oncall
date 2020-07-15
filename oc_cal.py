#!/usr/bin/env python3
# Create a year HTML calendar.

import sys
import calendar
import bs4
import datetime

def cal_save(oc_people, oc_sched_file, oc_web_dir):
    """Save the oncall schedule on a HTML file."""

    # Open files, and catch expection in case file doesn't exists.
    try:
        # Open calendar file from the current year.
        cal_year = datetime.datetime.now().year
        oc_cal_file = "{dir_cal}/oncall_sched_{year}.html".format(dir_cal=oc_web_dir, year=cal_year)

        # Open HTML file with calendar.
        with open(oc_cal_file) as fbs:
            soup = bs4.BeautifulSoup(fbs, 'html.parser')

        # We ignore the first tag 'table' because it's the year, we 
        # want only the months.
        tt_month = soup.find_all('table')[1:] 
        print(len(tt_month))
        
        for tt in tt_month:
            print(len(tt))
            print(tt.contents[0])
        # Open file file with the oncall schedule.
        with open(oc_sched_file,'r') as ff:
            text = ff.readlines()

        for line in text:
            line = line.strip()
            oc_user = line.split("|")[0].strip()
            oc_start = datetime.datetime.strptime(line.split("|")[1].strip(), 
                "%Y-%m-%d").date()
            oc_end = datetime.datetime.strptime(line.split("|")[2].strip(), 
                "%Y-%m-%d").date()

    except FileNotFoundError as not_found:
        print("Error opening file {}. Aborting...".format(not_found.filename))

    #print(oc_user, oc_start, oc_end)

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

