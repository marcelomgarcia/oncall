#!/usr/bin/env python3
# On-call management system.
# Marcelo Garcia
# May/2020.


import configparser as cfgp

def load_users(file_users):
    """Return a dictionary with the users definition: 
    name, phone, etc."""
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


if __name__ == "__main__":
    # Load users from file.
    oc_users = load_users('./files/oncall_people.cfg')

    print(oc_users)