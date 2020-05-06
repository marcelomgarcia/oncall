#!/usr/bin/env python3
# On-call management system.
# Marcelo Garcia
# May/2020.

import sys
import configparser as cfgp
import argparse as argp
import datetime

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
    

if __name__ == "__main__":
    # Load users from file.
    oc_users = load_users('files/oncall_people.cfg')
    oc_sched_file = "files/oncall_sched.txt"

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
    else:
        print("noo")
