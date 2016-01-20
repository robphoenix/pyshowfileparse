import os
import re
from pprint import pprint
from collections import namedtuple


FOLDER = "/home/willem/CLERK/files/example_show_files_dir"
HOSTNAME_REGEX = re.compile(r"(?P<hostname>\S+)\#sh[ow\s]+ver.*")
SERIAL_NUMBER_REGEX = re.compile(r"""
                                 [Ss]ystem\s+[Ss]erial\s+[Nn]umber
                                 \s+:\s
                                 (?P<sys_ser_num>[A-Z0-9]+)""",
                                 re.VERBOSE)
MODEL_AND_SOFTWARE_REGEX = re.compile(r"""
                                      (?P<model_num>[A-Z0-9-]+)
                                      \s+
                                      (?P<sw_ver>\d+.\d\(\d\)[A-Z\d]+)
                                      \s+
                                      (?P<sw_image>[a-zA-Z\d-]+)""",
                                      re.VERBOSE)


def _find_hostname(fin):
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


def _find_serial_nums(fin):
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


def _find_model_sw(fin):
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
    i, device_list = 0, []
    Device = namedtuple('Device',
                        'hostname serial_number model_number software_version software_image')
    for fin in os.listdir(FOLDER):
        hostname = _find_hostname(open(os.path.join(FOLDER, fin)))
        serial_numbers = _find_serial_nums(open(os.path.join(FOLDER, fin)))
        model_sw_result = _find_model_sw(open(os.path.join(FOLDER, fin)))
        while i < len(serial_numbers):
            device_list.append(Device(hostname,
                                      serial_numbers[i],
                                      model_sw_result[i][0],
                                      model_sw_result[i][1],
                                      model_sw_result[i][2]))
            i += 1
    return device_list


pprint(collate(FOLDER))
