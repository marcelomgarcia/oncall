#!/usr/bin/env python3
# On-call management system.
# Marcelo Garcia
# May/2020.

import sys
import configparser as cfgp
import argparse as argp

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

if __name__ == "__main__":
    # Load users from file.
    oc_users = load_users('./files/oncall_people.cfg')

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
            usage="oncall.py add user start end")
        parser.add_argument("user", help="Person doing the on-call")
        parser.add_argument("start", help="Start of the on-call")
        parser.add_argument("end", help="End of the on-call")
        args = parser.parse_args()
    elif sys.argv[0] == "save":
        parser = argp.ArgumentParser(prog="save", 
            description="Save HTML file with on-call calendar",
            usage="oncall.py save --file file_calendar.html")
        parser.add_argument("-f", "--file", help="HTML fileo")
        args = parser.parse_args()
    else:
        print("noo")
