# Auxiliary routines for the on-call system.
import configparser as cfgp


def load_config(oc_config_file):
    """Return the files used on on-call system"""
    oc_config = {}

    try:
        oc_parser = cfgp.ConfigParser()
        oc_parser.read(oc_config_file)
        defaults = oc_parser.defaults()
        
    except: 
        print("Error loading configuration.")
        defaults = {}

    return defaults