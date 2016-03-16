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
    Uses a regular expression. ## TODO improve find_hostname description

    Args:
        fin (str): Cisco show file ## TODO improve find_hostname args description

    Returns:
        tuple(str): Device hostname

    Example:
        >>> text = open("file.txt").read()
        >>> find_hostname(text)
        ('hostname',)
    """
    return (HOSTNAME_REGEX.search(text).group("hostname"),)


def find_serial_nums(text):
    """
    Finds device serial number(s) in a given Cisco 'show' file.
    Uses a regular expression. ## TODO improve find_serial_nums description.
    ## TODO Include note about needing to keep order, therefore set is not an option

    Args:
        fin (str): Cisco show file ## TODO improve find_serial_nums args description

    Returns:
        tuple(str): A list of device serial numbers

    Example:
        >>> text = open("file.txt").read()
        >>> find_serial_nums(text)
        ('ABC1111A11A', 'DEF2222D22D', 'XYZ3333X333')
    """
    sn_list = []
    serial_nums = re.findall(SERIAL_NUMBER_REGEX, text)
    [sn_list.append(item) for item in serial_nums if item not in sn_list]
    return tuple(sn_list)


def find_model_sw(text):
    """
    Finds model number, software version and software image
    in a given Cisco 'show' file.

    Uses a regular expression. ## TODO improve find_model_sw description

    Args:
        fin (str): Cisco show file. ## TODO improve find_model_sw args description

    Returns:
        tuple(tuple(str)): tuple of 3 string tuples, containing device
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
    Creates a list of named tuples. Each named tuple contains the
    hostname, serial number, model number, software version and
    software image for each Cisco 'show' file in a given directory.

    Args:
        directory (str): Directory containing the Cisco show files

    Returns:
        tuple(Device(str)): tuple of named tuples containing device
                           info strings.

    Example:
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
    """ TODO improve csv_inventory docstring
    Creates a .csv file containing Cisco device information from
    a given list of named tuples.

    Args:
        collated_records (iter(Device(str))): iterable of named tuples.

    Returns:
        IO -> A .csv file.
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


def width_of_column(collated_records, column, init_length):
    for entry in collated_records:
        col_length = len(getattr(entry, column))
        if col_length > init_length:
            init_length = col_length
    return init_length


def stdout_inventory(collated_records):
    hn_col = width_of_column(collated_records, "hostname", 8)
    sn_col = width_of_column(collated_records, "serial_number", 13)
    mn_col = width_of_column(collated_records, "model_number", 12)
    si_col = width_of_column(collated_records, "software_image", 14)
    sv_col = width_of_column(collated_records, "software_version", 16)
    table_structure = " | {0:<{hn_col}} | {1:^{sn_col}} | {2:<{mn_col}} | {3:<{si_col}} | {4:^{sv_col}} |"
    table_divider = " +-{0:-^{hn_col}}-+-{1:-^{sn_col}}-+-{2:-^{mn_col}}-+-{3:-^{si_col}}-+-{4:-^{sv_col}}-+".format(
        "", "", "", "", "", hn_col=hn_col, sn_col=sn_col, mn_col=mn_col, si_col=si_col, sv_col=sv_col)
    print("\n" + table_divider)
    print(table_structure.format("Hostname",
                                 "Serial Number",
                                 "Model Number",
                                 "Software Image",
                                 "Software Version",
                                 hn_col=hn_col,
                                 sn_col=sn_col,
                                 mn_col=mn_col,
                                 si_col=si_col,
                                 sv_col=sv_col))
    print(table_divider)
    for entry in collated_records:
        print(table_structure.format(entry.hostname,
                                     entry.serial_number,
                                     entry.model_number,
                                     entry.software_image,
                                     entry.software_version,
                                     hn_col=hn_col,
                                     sn_col=sn_col,
                                     mn_col=mn_col,
                                     si_col=si_col,
                                     sv_col=sv_col))
    print(table_divider + "\n")


if __name__ == '__main__':
	main()
