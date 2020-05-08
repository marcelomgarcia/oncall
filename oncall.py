#!/usr/bin/env python3
# On-call management system.
# Marcelo Garcia
# May/2020.

import sys
import configparser as cfgp
import argparse as argp
import datetime
import jinja2 as jj2
import ast
import requests
import json

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

def print_help():
    """Print a usage in case no argument is given, and exit"""
    print("""
    NEC on-call management system. 
    
    Usage:
    oncall.py <command>,
    were command is one of the following: 
    - add: add a new entry to the on-call schedule,
    - save: print on-call calendar to a HTML file,
    - now: create the 'on-call now' file for operators,
    - update: update the calendar and 'on-call now' file.

    For each option to a command use:
    oncall.py <command> -h
    
    """)

def oncall_add(oc_users, cmd_args):
    """Add an entry to on-call schedule. 'oc_users' is a dictionary with valid 
    users, and 'cmd_args' is the namespace with objects returned by 
    'argparser.parse_args'. The namespace should contain the 'user', 'start' 
    and 'end' of the on-call."""

    # Check if the user is valid.
    if cmd_args.user not in oc_users.keys():
        print("User {0} is invalid. Valid users are: {1}.".format(cmd_args.user, 
            ", ".join([kk for kk in oc_users.keys()])))
        return ""

    # Basic check of date consistency.
    today = datetime.date.today()
    oc_start = datetime.datetime.strptime(cmd_args.start, "%Y-%m-%d").date()
    oc_end = datetime.datetime.strptime(cmd_args.end, "%Y-%m-%d").date()
    if today > oc_start:
        print("On-call can't start in past. At least today!")
        return ""
    if oc_start > oc_end:
        print("On-call can't ends before it starts! Check dates.")
        return ""
    
    # After basic checks of user and dates, return the next entry
    return "{user} | {dt_start} | {dt_end}\n".format(user=cmd_args.user, 
        dt_start=oc_start.strftime("%Y-%m-%d"),
        dt_end=oc_end.strftime("%Y-%m-%d"))

def oc_sched_add(oc_file, oc_new_entry):
    """Add new entry 'oc_new_entry' to 'oc_file'. 'oc_file' is just a string
    with the name of the file to open and append the entry."""
    try:
        with open(oc_file, 'a') as fin:
            #fin.write(oc_new_entry + "\n")
            fin.write(oc_new_entry)
    except OSError:
        print("OS error with {0}".format(oc_file))
    except:
        print("Something went wrong with file {0}".format(oc_file))
    
def oc_now(oc_users, oc_sched, oncall_now_file):
    """Verify how is on-call now, and update system if there was change in 
    person on duty or dates."""

    # Open file with who is currently on call
    with open(oncall_now_file) as fnow:
        text = fnow.readline()
    now_user = text.split("|")[0].strip()
    now_start = datetime.datetime.strptime(text.split("|")[1].strip(), 
            "%Y-%m-%d").date()
    now_end = datetime.datetime.strptime(text.split("|")[2].strip(), 
            "%Y-%m-%d").date()

    today = datetime.date.today()

    # Scan schedule file for who should be on-call now.
    with open(oc_sched, 'r') as fsched:
        text = fsched.readlines()

    for line in text:
        oc_user = line.split("|")[0].strip()
        oc_start = datetime.datetime.strptime(line.split("|")[1].strip(), 
            "%Y-%m-%d").date()
        oc_end = datetime.datetime.strptime(line.split("|")[2].strip(), 
            "%Y-%m-%d").date()

        if oc_end > today and today > oc_start:
            break

    if not oc_users:
        print("Error! The oncall user is empty! Something very wrong here!!!")
        sys.exit(1)

    if oc_user != now_user or oc_start != now_start or oc_end != now_end:
        new_oc_now = "{user} | {dt_start} | {dt_end}\n".format(
            user=oc_user,
            dt_start=oc_start.strftime("%Y-%m-%d"),
            dt_end=oc_end.strftime("%Y-%m-%d")
        )
        with open(oncall_now_file, 'w') as fnow:
            fnow.write(new_oc_now)
        
        update_oncall_page(oc_users[oc_user])
        # Only change in Check-mk if the user has changed.
        if oc_user != now_user:
            update_cmk_sms(oc_user, oc_set=True)
            update_cmk_sms(now_user, oc_set=False)
    else:
        print("Current on-duty engineer: {}".format(oc_users[oc_user]['name']))
        print("Phone: {0}".format(oc_users[now_user]['phone']))
        print("From {dt_start} to {dt_end}".format(
            dt_start=now_start.strftime("%Y-%m-%d"),
            dt_end=now_end.strftime("%Y-%m-%d")))

def update_cmk_sms(oc_user, oc_set):
    """Add user to 'on-call' contact group so the engineer will receive 
    SMS from the notifications."""

    header = "{'action':'edit_users', '_username':'necbot', " + \
        "'_secret':'C@KPWKESBEES@EOOLAQE', 'request_format':'json'," + \
        "'output_format':'json', 'request': '{"
    if oc_set:
        user_payload   = '"users":{"' + oc_user + '"' + \
            ':{"set_attributes":{"contactgroups":["dwdos", "on-call"]}}}}' + "'}"
    else:
        user_payload   = '"users":{"' + oc_user + '"' + \
            ':{"set_attributes":{"contactgroups":["dwdos"]}}}}' + "'}"

    payload_str = header + user_payload

    edit_payload = ast.literal_eval(payload_str)

    cmk_url = 'http://localhost/mysite/check_mk/webapi.py'
    rr = requests.get(cmk_url, data=edit_payload)

    rr_json = json.loads(rr.text)
    ret_code = rr_json["result_code"]

    if ret_code != 0:
        print("Error while editing user {} in 'oncall' group".format(oc_user))
        print("Aborting the program")
        sys.exit(1)

    # Activate the change
    activate_payload = {
        'action':'activate_changes', 
        '_username':'necbot', 
        '_secret':'C@KPWKESBEES@EOOLAQE', 
        'request_format':'json','output_format':'json', 
        'request': '{"sites":["mysite"], "allow_foreign_changes":"1"}'}
    rr = requests.get(cmk_url, data=activate_payload)
    rr_json = json.loads(rr.text)
    ret_code = rr_json["result_code"]

    if ret_code != 0:
        print("Error while activating changes for user {}".format(oc_user))
        print("Aborting the program")
        sys.exit(1)


def update_oncall_page(oc_user):
    """Update web page for the operators with who is on-call now. The page
    contains the name and phone of engineer on duty."""
    www_dir = '/var/www/oncall/'
    file_loader = jj2.FileSystemLoader('templates')
    env = jj2.Environment(loader=file_loader)
    oc_template = env.get_template('oncall_now.j2')
    oc_page = oc_template.render(oc_vars=oc_user)
    with open(www_dir + 'oncall_now.html','w') as fpage:
        fpage.write(oc_page)

# 
# Main routine
#

if __name__ == "__main__":
    # Load users from file.
    oc_users = load_users('files/oncall_people.cfg')
    oc_sched_file = "files/oncall_sched.txt"
    on_call_now_file = "files/oncall_now.txt"

    # Check the number of arguments. If none was given, present an error 
    # message and leave. Or if an argument was given, shift the command 
    # line so the command becomes the program name (sys.argv[0]).
    if len(sys.argv) == 1:
        print_help()
    else:
        sys.argv = sys.argv[1:]

    # Create a custom command line depending of the option/cmmand given.
    if sys.argv[0] == "add":
        parser = argp.ArgumentParser( 
            description="Add a new entry to on-call schedule.",
            usage="oncall.py add user start end",
            epilog="Date format for 'start' and 'end': YYYY-MM-DD")
        parser.add_argument("user", help="Person doing the on-call")
        parser.add_argument("start", help="Start of the on-call")
        parser.add_argument("end", help="End of the on-call")
        args = parser.parse_args()
        oc_new_entry = oncall_add(oc_users, args)
        # Add entry to on-call schedule file.
        oc_sched_add(oc_sched_file, oc_new_entry)
    elif sys.argv[0] == "save":
        parser = argp.ArgumentParser(prog="save", 
            description="Save HTML file with on-call calendar",
            usage="oncall.py save --file file_calendar.html")
        parser.add_argument("-f", "--file", help="HTML fileo")
        args = parser.parse_args()
    elif sys.argv[0] == "now":
        # Who is on-call now?
        oc_now(oc_users, oc_sched_file, on_call_now_file)
    else:
        print("noo")
