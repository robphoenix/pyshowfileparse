import os
import re
import csv
from sys import argv
from collections import namedtuple
from time import gmtime, strftime

# script, DIRECTORY = argv
DIRECTORY = "/home/willem/code/python/cisco_clerk/test_data"
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
        (?P<sys_ser_num>[\w]+)            # capture serial number group
        """,
        re.VERBOSE)
MODEL_AND_SOFTWARE_REGEX = re.compile(
        r"""
        (?P<model_num>[\w-]+)               # capture model number group
        \s+                                 # separator
        (?P<sw_ver>\d{2}\.[\w\.)?(?]+)      # capture software version group
        \s+                                 # separator
        (?P<sw_image>\w+[-|_][\w-]+\-[\w]+) # capture software image group
        """,
        re.VERBOSE)


def find_hostname(fin):
    """
    find_hostname(file) -> str

    Finds device hostname in a given Cisco 'show' file.
    Uses a regular expression.


    >>> find_hostname(open("file.txt"))
    'hostname'
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
    find_serial_nums(file) -> list(str)

    Finds device serial number(s) in a given Cisco 'show' file.
    Uses a regular expression.


    >>> find_serial_nums(open("file.txt"))
    ['ABC1111A11A', 'DEF2222D22D', 'XYZ3333X333']
    """
    sn_list = []
    for line in fin:
        if SERIAL_NUMBER_REGEX.search(line):
            sn_match = re.match(SERIAL_NUMBER_REGEX, line).group("sys_ser_num")
            if sn_match not in sn_list:
                sn_list.append(sn_match)
    return sn_list

def find_model_sw(fin):
    """
    find_model_sw(file) -> list(tuple(str))

    Finds model number, software version and software image in a given Cisco 'show' file.
    Uses a regular expression.


    >>> find_model_sw(open("file.txt"))
    [('WS-C2960X-48FPD-L', '15.0(2)EX5', 'C2960X-UNIVERSALK9-M'),
     ('WS-C2960X-48FPD-L', '15.0(2)EX5', 'C2960X-UNIVERSALK9-M'),
     ('WS-C2960X-24PD-L', '15.0(2)EX5', 'C2960X-UNIVERSALK9-M')]
    """
    model_sw_list = re.findall(MODEL_AND_SOFTWARE_REGEX, fin.read())
    return model_sw_list


def collate(directory):
    """
    collate(str) -> list(Device(str))

    Creates a list of named tuples. Each named tuple contains the hostname,
    serial number, model number, software version and software image for
    each Cisco 'show' file in a given directory.


    >>> collate("directory")
    [Device(hostname='elizabeth_cotton',
            serial_number='ANC1111A1AB',
            model_number='WS-C2960C-8PC-L',
            software_version='15.0(2)SE5',
            software_image='C2960c405-UNIVERSALK9-M'),
     Device(hostname='howlin_wolf',
            serial_number='ABC2222A2AB',
            model_number='WS-C2960C-8PC-L',
            software_version='15.0(2)SE5',
            software_image='C2960c405-UNIVERSALK9-M')]
    """
    device_list = []
    Device = namedtuple('Device',
                        '''hostname
                           serial_number
                           model_number
                           software_version
                           software_image''')
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


def csv_inventory(collated_records):
    """
    Creates a .csv file containing Cisco device information from
    a given list of named tuples.
    """
    csv_filename = "INVENTORY-{}.csv".format(
        strftime("%Y-%m-%d-%H%M%S", gmtime()))
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


# csv_inventory(collate(DIRECTORY))
collate(DIRECTORY)
