# Auxiliary routines for the on-call system.

import sys
import configparser as cfgp
import argparse as argp
import datetime
import jinja2 as jj2
import ast
import requests
import json

def print_help():
    """Print a usage in case no argument is given, and exit"""
    print("""
    NEC on-call management system. 
    
    Usage:
    oncall.py <command>,
    were command is one of the following: 
    - add: add a new entry to the on-call schedule file,
    - now: print the 'on-call now' person,
    - update: update on-call now information: operatos and Check-mk,
    - calendar: print on-call schedule as a HTML file.

    For each option to a command use:
    oncall.py <command> -h
    
    """)

def sched_new_get(cmd_args):
    """Return a dictiorany with 'user', 'start' and 'end' as define in 
    Namespace 'cmd_args'."""

    return {'user': cmd_args.user, 
        'start': datetime.datetime.strptime(cmd_args.start, "%Y-%m-%d").date(),
        'end': datetime.datetime.strptime(cmd_args.end, "%Y-%m-%d").date()}

def load_config(oc_config_file):
    """Return the files used on on-call system"""

    try:
        oc_parser = cfgp.ConfigParser()
        oc_parser.read(oc_config_file)
        oncall_items = dict(oc_parser.items('ONCALL'))
        
    except: 
        print("Error loading configuration.")
        oncall_items = {}
    finally:
        return oncall_items

def load_users(file_users):
    """Return a dictionary with the users definition: 
    name, phone, and email."""
    users = {}
    # Create a dictionary with user info.
    try:
        config_users = cfgp.ConfigParser()
        config_users.read(file_users)
        for ss in config_users.sections():
            users[ss] = {
                'name': config_users.get(ss, 'name'), 
                'phone': config_users.get(ss, 'phone'), 
                'email': config_users.get(ss, 'email')
            }
    except:
        print("Error loading users from file")
        # Reset the users.
        users = {}
    finally:
        # Return 'users'. Empty in case of error.
        return users

def oncall_sched_get(oc_sched_file):
    """Return the user who is scheduled to be on call now according to the 
    'oc_sched_file'."""

    today = datetime.date.today()

    # Scan schedule file for who should be on-call now.
    with open(oc_sched_file, 'r') as fsched:
        text = fsched.readlines()

    for line in text:
        oc_user = line.split("|")[0].strip()
        oc_start = datetime.datetime.strptime(line.split("|")[1].strip(), 
            "%Y-%m-%d").date()
        oc_end = datetime.datetime.strptime(line.split("|")[2].strip(), 
            "%Y-%m-%d").date()

        if oc_end >= today and today >= oc_start:
            break

    if not oc_user:
        print("Error! The oncall user is empty! Something very wrong here!!!")
        return {}
    else:
        return {'user': oc_user, 'start': oc_start, 'end': oc_end}

def oncall_now_get(oncall_now_file):
    """Return the on-call user."""

    # Open file with who is currently on call
    with open(oncall_now_file) as fnow:
        text = fnow.readline()
    now_user = text.split("|")[0].strip()
    now_start = datetime.datetime.strptime(text.split("|")[1].strip(), 
            "%Y-%m-%d").date()
    now_end = datetime.datetime.strptime(text.split("|")[2].strip(), 
            "%Y-%m-%d").date()

    return {'user': now_user, 'start': now_start, 'end': now_end}

def is_sched(sched_new, oc_users):
    """Basic check for new entry for the on-call schedule file: if the user 
    is define, start of on-call is not in the past or if it's not ending
    before starting."""

    today = datetime.date.today()

    if sched_new['user'] not in oc_users.keys():
        print("User {0} is invalid. Valid users are: {1}.".format(
            sched_new['user'],", ".join(
                [kk for kk in oc_users.keys()]
                )
            ))
        return False
    elif today > sched_new['start']:
        print("On-call can't start in past. At least today!")
        return False
    elif sched_new['start'] > sched_new['end']:
        print("End date can't be older than start date! Check dates.")
        return False
    else:
        return True

def oncall_sched_add(oc_sched_file, sched_new):
    """Add entry in 'sched_new' to on-call schedule file, 'oc_sched_file."""

    oc_new_sched = "{user} | {dt_start} | {dt_end}\n".format(
        user=sched_new['user'],
        dt_start=sched_new['start'].strftime("%Y-%m-%d"),
        dt_end=sched_new['end'].strftime("%Y-%m-%d")
    )
    try:
        with open(oc_sched_file, 'a') as fin:
            fin.write(oc_new_sched)
    except OSError:
        print("OS error with {0}".format(oc_sched_file))
    except:
        print("Something went wrong with file {0}".format(oc_sched_file))

def oncall_now_print(oc_users, now_user):
    """Print user doing the on-call now."""
    user_name = oc_users[now_user['user']]['name']
    user_phone = oc_users[now_user['user']]['phone']

    print("On-call now:")
    print("{}, {}.".format(user_name, user_phone))
    print("From {}, until {}".format(
        now_user['start'].strftime("%a, %d %B %Y"),
        now_user['end'].strftime("%a, %d %B %Y")
    ))

def oncall_now_set(sched_user, oncall_now_file):
    """Update the 'oncall now' file with scheduled user."""

    sched_user_str = "{user} | {dt_start} | {dt_end}\n".format(
        user=sched_user['user'],
        dt_start=sched_user['start'].strftime("%Y-%m-%d"),
        dt_end=sched_user['end'].strftime("%Y-%m-%d"))

    with open(oncall_now_file, 'w') as fsched:
        fsched.write(sched_user_str)
    
def oncall_update_webpage(sched_user_contact, oc_now_page):
    """Update web page for the operators with who is on-call now. The page
    contains the name and phone of engineer on duty."""

    file_loader = jj2.FileSystemLoader('templates')
    env = jj2.Environment(loader=file_loader)
    oc_template = env.get_template('oncall_now.j2')
    oc_page = oc_template.render(oc_vars=sched_user_contact)
    with open(oc_now_page,'w') as fpage:
        fpage.write(oc_page)

def oncall_update(sched_user, now_user, oc_users, oc_now_file, oc_now_page):
    """Update 'now' file, page for the operators and Check-mk on call user
    with new information for 'sched_user'"""

    # If there is a difference between the scheduled user and the one that
    # is doing now, update the "now" part.
    if sched_user['user'] != now_user['user'] or \
        sched_user['start'] != now_user['start'] or \
        sched_user['end'] != now_user['end']:

        print("Updating 'oncall now' user with 'scheduled' info...")
        print("Current: {}, {}, {}".format(
            now_user['user'],
            now_user['start'].strftime("%Y-%m-%d"),
            now_user['end'].strftime("%Y-%m-%d")
        ))
        print("New    : {}, {}, {}".format(
            sched_user['user'],
            sched_user['start'].strftime("%Y-%m-%d"),
            sched_user['end'].strftime("%Y-%m-%d")
        ))
        print("Updating 'oncall now' file...", end=" ")
        oncall_now_set(sched_user, oc_now_file)
        print("done")

        print("Updating 'oncall now' webpage...", end=" ")
        oncall_update_webpage(oc_users[sched_user['user']], oc_now_page)
        print("done")
    else:
        print("Nothing to update")