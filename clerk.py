#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Cisco Clerk

This module contains functions to extract device info from Cisco Switch `show` files.
## TODO improve module description

Example:
    ## TODO improve example description
    $ python clerk.py show_files_directory

Attributes:
    HOSTNAME_REGEX (str): Regex to extract the device hostname.
                          Matches: HOSTNAME#sh version
                          Assumes the `show version` command is used in
                          the config. files, and the hostname is the name
                          before the # symbol.
    SERIAL_NUMBER_REGEX (str): Regex to extract the device serial number.
                               Matches: System serial number            : ABC2016XYZ
    MODEL_SW_PATTERN (str): Regex to extract device model number,
                            software version and software image.
                            Matches: WS-C2960C-8PC-L    15.0(2)SE5            C2960c405-UNIVERSALK9-M
                            Matches: WS-C3650-24TD      03.03.03SE        cat3k_caa-universalk9 INSTALL
"""

import os
import re
import json
from collections import namedtuple


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

def find_hostname(text):
    """
    Finds device hostname in a given Cisco 'show' file.
    Uses a regular expression. ## TODO improve find_hostname description

    Args:
        fin (str): Cisco show file

    Returns:
        hostname (tuple(str)): Device Hostname

    Example:
        >>> text = open('./test_data/elizabeth_cotton.txt').read()
        >>> find_hostname(text)
        ('elizabeth_cotton',)
    """
    hostname = (HOSTNAME_REGEX.search(text).group('hostname'),)
    return hostname


def find_serial_nums(text):
    """
    Finds device serial number(s) in a given Cisco 'show' file.
    Uses a regular expression. ## TODO improve find_serial_nums description.
    ## TODO Include note about needing to keep order, therefore set is not an option

    Args:
        fin (str): Cisco show file

    Returns:
        serial_numbers (tuple(str)): Device Serial Numbers

    Example:
        >>> text = open('./test_data/lightning_hopkins.txt').read()
        >>> find_serial_nums(text)
        ('ABC3333A33A', 'ABC4444A44A', 'ABC5555A555')
    """
    sn_list = []
    sn_matches = re.findall(SERIAL_NUMBER_REGEX, text)
    [sn_list.append(item) for item in sn_matches if item not in sn_list]
    serial_numbers = tuple(sn_list)
    return serial_numbers


def find_model_sw(text):
    """
    Finds model number, software version and software image
    in a given Cisco 'show' file.

    Uses a regular expression.

    Args:
        fin (str): Cisco show file.

    Returns:
        model_and_software (tuple(tuple(str))): Device model number, software version and software image

    Example:
        >>> text = open('./test_data/lightning_hopkins.txt').read()
        >>> find_model_sw(text)
        (('WS-C2960X-48FPD-L', '15.0(2)EX5', 'C2960X-UNIVERSALK9-M'), ('WS-C2960X-48FPD-L', '15.0(2)EX5', 'C2960X-UNIVERSALK9-M'), ('WS-C2960X-24PD-L', '15.0(2)EX5', 'C2960X-UNIVERSALK9-M'))
    """
    model_and_software = tuple(re.findall(MODEL_AND_SOFTWARE_REGEX, text))
    return model_and_software


def collate(directory):
    """
    Creates a list of named tuples. Each named tuple contains the
    hostname, serial number, model number, software version and
    software image for each Cisco 'show' file in a given directory.

    Args:
        directory (str): Directory containing the Cisco show files

    Returns:
        devices (tuple(Device(str))): tuple of named tuples containing device attributes

    Example:
        >>> collate('./test_data')
        (Device(hostname='elizabeth_cotton', serial_number='ANC1111A1AB', model_number='WS-C2960C-8PC-L', software_version='15.0(2)SE5', software_image='C2960c405-UNIVERSALK9-M'), Device(hostname='howlin_wolf', serial_number='ABC2222A2AB', model_number='WS-C2960C-8PC-L', software_version='15.0(2)SE5', software_image='C2960c405-UNIVERSALK9-M'), Device(hostname='lightning_hopkins', serial_number='ABC3333A33A', model_number='WS-C2960X-48FPD-L', software_version='15.0(2)EX5', software_image='C2960X-UNIVERSALK9-M'), Device(hostname='lightning_hopkins', serial_number='ABC4444A44A', model_number='WS-C2960X-48FPD-L', software_version='15.0(2)EX5', software_image='C2960X-UNIVERSALK9-M'), Device(hostname='lightning_hopkins', serial_number='ABC5555A555', model_number='WS-C2960X-24PD-L', software_version='15.0(2)EX5', software_image='C2960X-UNIVERSALK9-M'), Device(hostname='sister_rosetta_tharpe', serial_number='ABC6666A6AB', model_number='WS-C3650-24TD', software_version='03.03.03SE', software_image='cat3k_caa-universalk9'))
    """
    device_list = []
    Device = namedtuple('Device',
                        '''hostname
                           serial_number
                           model_number
                           software_version
                           software_image''')
    for fin in sorted(os.listdir(directory)):
        with open(os.path.join(directory, fin)) as show_f:
            content = show_f.read()
            hostname = find_hostname(content)
            serial_numbers = find_serial_nums(content)
            model_sw_result = find_model_sw(content)
            i = 0
            while i < len(serial_numbers):
                device_list.append(Device(hostname[0],
                                          serial_numbers[i],
                                          model_sw_result[i][0],
                                          model_sw_result[i][1],
                                          model_sw_result[i][2]))
                i += 1
    devices = tuple(device_list)
    return devices


def csv_inventory(collated_records):
    """
    Creates a .csv formatted string containing Cisco device information from
    a given list of named tuples.

    Args:
        collated_records (iter(Device(str))): iterable of named tuples.

    Returns:
        output (str): CSV formatted string
    """
    output = ','.join(list(collated_records[0]._fields))

    for record in collated_records:
        output += '\n'
        output += ','.join(list(record))
    return output



def json_inventory(collated_records):
    dict_records = [named_tuple_to_dict(record) for record in collated_records]
    return json.dumps(dict_records)

def named_tuple_to_dict(nt):
    return dict(zip(nt._fields, list(nt)))


def width_of_column(collated_records, column, init_length):
    for entry in collated_records:
        col_length = len(getattr(entry, column))
        if col_length > init_length:
            init_length = col_length
    return init_length


def ascii_table_inventory(collated_records):
    hn_col = width_of_column(collated_records, "hostname", 8)
    sn_col = width_of_column(collated_records, "serial_number", 13)
    mn_col = width_of_column(collated_records, "model_number", 12)
    si_col = width_of_column(collated_records, "software_image", 14)
    sv_col = width_of_column(collated_records, "software_version", 16)
    table_structure = " | {0:<{hn_col}} | {1:^{sn_col}} | {2:<{mn_col}} | {3:<{si_col}} | {4:^{sv_col}} |"
    table_divider = " +-{0:-^{hn_col}}-+-{1:-^{sn_col}}-+-{2:-^{mn_col}}-+-{3:-^{si_col}}-+-{4:-^{sv_col}}-+".format(
        "", "", "", "", "", hn_col=hn_col, sn_col=sn_col, mn_col=mn_col, si_col=si_col, sv_col=sv_col)
    output = '\n'
    output += table_divider
    output += '\n'

    output += table_structure.format(
        "Hostname",
        "Serial Number",
        "Model Number",
        "Software Image",
        "Software Version",
        hn_col=hn_col,
        sn_col=sn_col,
        mn_col=mn_col,
        si_col=si_col,
        sv_col=sv_col)

    output += '\n'
    output += table_divider
    output += '\n'

    for entry in collated_records:
        output += table_structure.format(
            entry.hostname,
            entry.serial_number,
            entry.model_number,
            entry.software_image,
            entry.software_version,
            hn_col=hn_col,
            sn_col=sn_col,
            mn_col=mn_col,
            si_col=si_col,
            sv_col=sv_col)
        output += '\n'

    output += table_divider
    output += '\n'
    return output
