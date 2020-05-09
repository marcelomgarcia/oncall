#!/usr/bin/env python3
# On-call management system.
# Marcelo Garcia
# May/2020.

import oc_lib
import sys
import argparse as argp

# 
# Main routine
#

if __name__ == "__main__":

    # Load configuration for the system.
    oc_config_file='files/oncall_config.cfg'
    oc_config = oc_lib.load_config(oc_config_file)

    if not oc_config:
        print("Configuration dict is empty!")
        print("Check 'load_config' function.")
        sys.exit(1)

    # Load users from file.
    oc_users = oc_lib.load_users(oc_config['oc_people_file'])
    if not oc_users:
        print("Users dict is empty!")
        print("Check 'load_users' function.")
        sys.exit(1)

    # Get the user scheduled to be on-call now. This is can be different
    # from the actual person doing the on-call now. In case of change it's
    # the job of function 'update' to update the 'on-call now', Check-mk 
    # and the page for the operators.
    sched_user = oc_lib.oncall_sched_get(oc_config['oc_sched_file'])
    if not sched_user:
        print("Scheduled user dict is empty!")
        print("Check 'oncall_sched_get' function.")
        sys.exit(1)

    # Actual on-call user now
    now_user = oc_lib.oncall_now_get(oc_config['oc_now_file'])

    # Check the number of arguments. If none was given, present an error 
    # message and leave. Or if an argument was given, shift the command 
    # line so the command becomes the program name (sys.argv[0]).
    if len(sys.argv) == 1:
        oc_lib.print_help()
    else:
        sys.argv = sys.argv[1:]

    # Create a custom command line depending of the option/cmmand given.
    if sys.argv[0] == "add":
        parser = argp.ArgumentParser( 
            description="Add a new entry to on-call schedule.",
            usage="oncall.py add 'user' 'start' 'end'",
            epilog="Date format for 'start' and 'end': YYYY-MM-DD")
        parser.add_argument("user", help="Person doing the on-call")
        parser.add_argument("start", help="Start of the on-call")
        parser.add_argument("end", help="End of the on-call")
        args = parser.parse_args()
        # Convert 'args' to dictiornary.
        sched_new = oc_lib.sched_new_get(args)
        # Check if new entry is valid.
        if oc_lib.is_sched(sched_new, oc_users):
            # Add entry to on-call schedule file.
            oc_lib.oncall_sched_add(oc_config['oc_sched_file'], sched_new)
            print("Added new entry to schedule file '{0}'".format(
                oc_config['oc_sched_file']
            ))
        else:
            print("Entry for schedule file is invalid.")
            sys.exit(1)
    elif sys.argv[0] == "now":
        # Who is on-call now?
        oc_lib.oncall_now_print(oc_users, now_user)
    elif sys.argv[0] == "update":
        oc_lib.oncall_update(sched_user,now_user, oc_users, 
        oc_config['oc_now_file'], oc_config['oc_now_page'])
    elif sys.argv[0] == "save":
        parser = argp.ArgumentParser(
            description="Save HTML file with on-call calendar",
            usage="oncall.py save --file file_calendar.html")
        parser.add_argument("-f", "--file", help="HTML fileo")
        args = parser.parse_args()
    else:
        print("noo")
