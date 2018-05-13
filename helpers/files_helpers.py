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
        print("""You didn't provided any YAML configuration file. You have the following options:

- Create it were you want and pass it with the '\033[1m-y\033[0m' parameter (\033[1mfiofly -y <path/to/the_file.yml>\033[0m)
- Create it just for your user in '\033[1m~/.config/fiofly/fiofly.yml\033[0m' (\033[1mrecommended\033[0m)
- Create it for all the users in '\033[1m/etc/fiofly/fiofly.yml\033[0m'

The program is just going to read one file. The previous list was in the order that the program is going to read them""")
        sys.exit(1)
