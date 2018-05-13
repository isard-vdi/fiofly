#!/usr/bin/env python3
#
# Albeto Larraz Dalmases
# Néfix Estrada Campañá
# IsardVDI Project
# Escola del Treball de Barcelona

# Imports
import os
import sys
import yaml


def read_yaml_file(path):
    with open(path) as file:
        conf = yaml.safe_load(file)

    return conf


def get_yaml_file_config(args):
    """
    Get the file that the program is going to use.
    """
    user_yaml_file = os.path.join(os.path.expanduser("~"), ".config", "fiofly", "fiofly.yml")
    system_yaml_file = os.path.abspath("/etc/fiofly/fiofly.yml")

    if args.yaml_file_conf:
        local_yaml_file = os.path.abspath(args.yaml_file_conf)

        if os.path.exists(local_yaml_file):
            return read_yaml_file(local_yaml_file)

        else:
            print("Sorry! The YAML file you specified with the '-y' parameter wasn't found!")

    elif os.path.exists(user_yaml_file):
        return read_yaml_file(user_yaml_file)

    elif os.path.exists(system_yaml_file):
        return read_yaml_file(system_yaml_file)

    else:
        print("You didn't provided any YAML file. You can create it where you want and pass it with the '-y' parameter, create it for your user in '~/.config/fiofly/fiofly.yml' or for all the users in '/etc/fiofly/fiofly.yml'")
        sys.exit(1)
