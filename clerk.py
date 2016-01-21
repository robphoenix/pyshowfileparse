import os
import re
import csv
from sys import argv
from collections import namedtuple
from time import gmtime, strftime

# script, DIRECTORY = argv
DIRECTORY = "/home/willem/code/python/cisco_clerk/example_show_files_dir"
HOSTNAME_REGEX = re.compile(
        r"""
        (?P<hostname>\S+) # capture hostname group
        \#                # Priviliged mode CLI prompt
        sh[ow\s]+ver.*    # show version pattern
        """,
        re.VERBOSE)
SERIAL_NUMBER_REGEX = re.compile(
        r"""
        [Ss]ystem\s+[Ss]erial\s+[Nn]umber # system serial number pattern
        \s+:\s                            # separator
        (?P<sys_ser_num>[A-Z0-9]+)        # capture serial number group
        """,
        re.VERBOSE)
MODEL_AND_SOFTWARE_REGEX = re.compile(
        r"""
        (?P<model_num>[A-Z0-9-]+)        # capture model number group
        \s+                              # separator
        (?P<sw_ver>\d{2}\.[A-Z\d\.)?(?]+) # capture software version group
        \s+                              # separator
        (?P<sw_image>[a-zA-Z0-9]+[-|_][a-zA-Z\d-]+\-[a-zA-Z0-9]+) # capture software image group
        """,
        re.VERBOSE)


def find_hostname(fin):
    """
    Finds device hostname in a given Cisco 'show' file.
    Uses a regular expression.
    """
    i, hostname = 0, ""
    while i < 1:
        for line in fin:
            if HOSTNAME_REGEX.search(line):
                hostname = re.match(HOSTNAME_REGEX, line).group("hostname")
                # finish parsing the file once hostname has been found
                i += 1
    return hostname


def find_serial_nums(fin):
    """
    Finds device serial number(s) in a given Cisco 'show' file.
    Uses a regular expression.
    """
    # as there may be more than one serial number, store them in a list
    sn_list = []
    for line in fin:
        if SERIAL_NUMBER_REGEX.search(line):
            sn_match = re.match(SERIAL_NUMBER_REGEX, line).group("sys_ser_num")
            if sn_match not in sn_list:
                sn_list.append(sn_match)
    return sn_list


def find_model_sw(fin):
    """
    Finds model number and software information in a given Cisco 'show' file.
    Uses a regular expression.
    """
    return re.findall(MODEL_AND_SOFTWARE_REGEX, fin.read())


def collate(directory):
    """
    Creates a list of named tuples. Each named tuple contains the hostname,
    serial number, model number, software version and software image for
    each Cisco 'show' file in a given directory.
    """
    device_list = []
    Device = namedtuple('Device',
                        'hostname serial_number model_number software_version software_image')
    for fin in sorted(os.listdir(directory)):
        hostname = find_hostname(open(os.path.join(directory, fin)))
        serial_numbers = find_serial_nums(open(os.path.join(directory, fin)))
        model_sw_result = find_model_sw(open(os.path.join(directory, fin)))
        i = 0
        while i < len(serial_numbers):
            device_list.append(Device(hostname,
                                      serial_numbers[i],
                                      model_sw_result[i][0],
                                      model_sw_result[i][1],
                                      model_sw_result[i][2]))
            i += 1
    return device_list


def csv_inventory_record(collated_records):
    """
    Creates a .csv file containing Cisco device information from
    a given list of named tuples.
    """
    csv_filename = "INVENTORY-{}.csv".format(strftime("%Y-%m-%d-%H%M%S", gmtime()))
    with open(csv_filename, 'w') as csvfile:
        fieldnames = ['Hostname',
                      'Serial Number',
                      'Model Number',
                      'Software Image',
                      'Software Version']
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(fieldnames)
        for entry in collated_records:
            writer.writerow([entry.hostname,
                            entry.serial_number,
                            entry.model_number,
                            entry.software_image,
                            entry.software_version])




csv_inventory_record(collate(DIRECTORY))
