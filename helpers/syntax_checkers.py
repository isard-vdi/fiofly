#!/usr/bin/env python3
#
# Albeto Larraz Dalmases
# Néfix Estrada Campañá
# IsardVDI Project
# Escola del Treball de Barcelona

# Imports
import sys
import yaml


def check_fio_destination(conf):
    """
    Check if there's a valid destination for the fio (and just one)
    """
    for test in conf["tests"]:
        test_name = [test_name for test_name in test.keys()][0]
        test = test[test_name]

        if "dir_to_fio" in test and "filename" in test:
            print("You have an error in your YAML file! You can't have both 'dir_to_fio' and 'filename'!")
            print("Error in the '\033[1m{}\033[0m' test".format(test_name))
            return False

        elif "dir_to_fio" not in test and "filename" not in test:
            print("You have an error in your YAML file! You need to add at least one target for the fio (use 'dir_to_fio' or 'filename')")
            print("Error in the '\033[1m{}\033[0m' test".format(test_name))
            return False

    return True


def check_syntax(conf):
    """
    Check the syntax of the YAML configuration file
    """
    if not check_fio_destination(conf):
        sys.exit(1)
