#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Title:      Cisco Clerk
Author:     Rob Phoenix (rob.phoenix@bt.com)
Usage:      Creates a CSV inventory of Cisco switches from a folder containing
            Cisco 'show version' text files.  This inventory contains the
            hostname, model number, serial number, software image & software version
            of each device, including switch stacks.
Date:       27/01/2016
Version:    0.1
Attributes:
    HOSTNAME_REGEX (str):      Regex to extract the device hostname.

                               Matches: HOSTNAME#sh version

                               Assumes the `show version` command is used in
                               the config. files, and the hostname is the name
                               before the # symbol.
    SERIAL_NUMBER_REGEX (str): Regex to extract the device serial number.

                               Matches: System serial number            : ABC2016XYZ

    MODEL_SW_PATTERN (str):    Regex to extract device model number,
                               software version and software image.

                               Matches: WS-C2960C-8PC-L    15.0(2)SE5            C2960c405-UNIVERSALK9-M
                               Matches: WS-C3650-24TD      03.03.03SE        cat3k_caa-universalk9 INSTALL
"""


import os
import re
import csv
import argparse
from collections import namedtuple
from time import gmtime, strftime
from gooey import Gooey, GooeyParser


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


@Gooey
def main():
    parser = GooeyParser(
        prog="Clerk",
        description="""
        Extract specific information from a directory of Cisco switch 'Show Files'.
        Prints to stdout unless filetype specified.""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Clerk
        =====

        Filing your Cisco inventory records
        -----------------------------------
        Generates an inventory of specific information regarding Cisco switches from a
        folder of text files containing the output of Cisco Show commands.
        This information can include, but is not limited to, device hostnames, model
        numbers, serial numbers, software image & version and site id's & names. Also
        takes into consideration switch stacks as well as individual switches.  This
        can then all be collated into a separate text file, csv file or excel
        spreadsheet, and updated as necessary if new files are added to the original
        folder. Currently, due to the individual nature of device naming conventions
        and engineer requirements, this project is not general purpose but built in a
        bespoke manner.  The more iterations this tool goes throught the more reusable
        it's parts will become.
        """)
    parser.add_argument("directory",
                        widget="DirChooser",
                        help="Specify the directory containing your 'Show Files'")
    args = parser.parse_args()

    csv_inventory(collate(args.directory))


def find_hostname(text):
    """
    Finds device hostname in a given Cisco 'show' file.

    Args:
        text (str): Cisco 'show' file as a string.

    Returns:
        tuple(str,): Device hostname.

    Example:
        >>> text = open("file.txt").read()
        >>> find_hostname(text)
        ('hostname',)
    """
    return (HOSTNAME_REGEX.search(text).group("hostname"),)


def find_serial_nums(text):
    """
    Finds device serial number(s) in a given Cisco 'show' file.

    Args:
        text (str): Cisco 'show' file as a string.

    Returns:
        tuple(str,): A tuple of device serial numbers.

    Example:
        >>> text = open("file.txt").read()
        >>> find_serial_nums(text)
        ('ABC1111A11A', 'DEF2222D22D', 'XYZ3333X333')
    """
    sn_list = []
    serial_nums = re.findall(SERIAL_NUMBER_REGEX, text)
    # One or more serial numbers may be duplicated within the file
    # so we need to remove any duplicates, but also preserve the order
    # in which the serial numbers are found, so tha the right serial number
    # is matched to the other relevant device info.  Therefore we can't
    # use a `set` as it doesn't preserve order.
    [sn_list.append(item) for item in serial_nums if item not in sn_list]
    return tuple(sn_list)


def find_model_sw(text):
    """
    Finds model number, software version and software image
    in a given Cisco 'show' file.

    Args:
        text (str): Cisco 'show' file as a string.

    Returns:
        tuple(tuple(str,),): Tuple of 3 string tuples, containing device
                             model number, software version and software image

    Example:
        >>> text = open("file.txt").read()
        >>> find_model_sw(text)
        [('WS-C2960X-48FPD-L', '15.0(2)EX5', 'C2960X-UNIVERSALK9-M'),
         ('WS-C2960X-48FPD-L', '15.0(2)EX5', 'C2960X-UNIVERSALK9-M'),
         ('WS-C2960X-24PD-L', '15.0(2)EX5', 'C2960X-UNIVERSALK9-M')]
    """
    return tuple(re.findall(MODEL_AND_SOFTWARE_REGEX, text))


def collate(directory):
    """
    Creates a tuple of named tuples. Each named tuple contains the
    hostname, serial number, model number, software version and
    software image for each device in a Cisco 'show' file within a
    given directory.

    Args:
        directory (str): Directory containing the Cisco show files.

    Returns:
        tuple(Device(str),): Tuple of named tuples containing device
                             info strings.

    Example:
        >>> collate("relative_directory_name")
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
    return tuple(device_list)


def csv_inventory(collated_records):
    """
    Creates a .csv file containing Cisco device information from
    a given iterable of named tuples. This is a dead-end function,
    it doesn't return anything, and has side-effects; writing to
    a .csv file.

    Args:
        collated_records (iter(Device(str),)): Iterable of named tuples.

    Returns:
        None
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


if __name__ == '__main__':
    main()
