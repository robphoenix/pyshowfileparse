import os
import re
from pprint import pprint
from collections import namedtuple


FOLDER = "~/CLERK/files/example_show_files_dir"
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
    i, hostname = 0, ""
    for line in fin:
        if HOSTNAME_REGEX.search(line):
            while i < 1:
                hostname = re.match(HOSTNAME_REGEX, line).group("hostname")
                i += 1
    return hostname


def _find_serial_nums(fin):
    sn_list = []
    for line in fin:
        if SERIAL_NUMBER_REGEX.search(line):
            sn_match = re.match(SERIAL_NUMBER_REGEX, line).group("sys_ser_num")
            if sn_match not in sn_list:
                sn_list.append(sn_match)
    return sn_list


def _find_model_sw(fin):
    return re.findall(MODEL_AND_SOFTWARE_REGEX, fin.read())


def collate(directory):
    device_list = []
    Device = namedtuple('Device',
                        'hostname serial_number model_number software_version software_image')
    for fin in os.listdir(FOLDER):
        i = 0
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

