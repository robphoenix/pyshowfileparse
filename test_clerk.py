import os
import shutil
from collections import namedtuple
import unittest

import clerk


Device = namedtuple('Device',
                    '''hostname
                       serial_number
                       model_number
                       software_version
                       software_image''')


class ClerkTest(unittest.TestCase):

    def setUp(self):
        self.test_data_dir = os.path.join(os.getcwd(), "test_data/")
        shutil.rmtree(os.path.join(
            self.test_data_dir, ".cache/"), ignore_errors=True)

    def test_fetch_hostname(self):
        expected = [('elizabeth_cotton',),
                    ('howlin_wolf',),
                    ('lightning_hopkins',),
                    ('sister_rosetta_tharpe',)]
        actual = []
        for fin in sorted(os.listdir(self.test_data_dir)):
            with open(os.path.join(self.test_data_dir, fin)) as t_fin:
                actual.append(clerk.fetch_hostname(t_fin.read()))
        self.assertEqual(actual, expected)

    def test_fetch_serial_nums(self):
        expected = [('ANC1111A1AB',),
                    ('ABC2222A2AB',),
                    ('ABC3333A33A', 'ABC4444A44A', 'ABC5555A555'),
                    ('ABC6666A6AB',)]
        actual = []
        for fin in sorted(os.listdir(self.test_data_dir)):
            with open(os.path.join(self.test_data_dir, fin)) as t_fin:
                actual.append(clerk.fetch_serial_nums(t_fin.read()))
        self.assertEqual(actual, expected)

    def test_fetch_model_sw(self):
        expected = [(('WS-C2960C-8PC-L',
                      '15.0(2)SE5',
                      'C2960c405-UNIVERSALK9-M'),),
                    (('WS-C2960C-8PC-L',
                      '15.0(2)SE5',
                      'C2960c405-UNIVERSALK9-M'),
                     ('WS-C2960C-8PC-L',
                      '15.0(2)SE5',
                      'C2960c405-UNIVERSALK9-M')),
                    (('WS-C2960X-48FPD-L',
                      '15.0(2)EX5',
                      'C2960X-UNIVERSALK9-M'),
                     ('WS-C2960X-48FPD-L',
                      '15.0(2)EX5',
                      'C2960X-UNIVERSALK9-M'),
                     ('WS-C2960X-24PD-L',
                      '15.0(2)EX5',
                      'C2960X-UNIVERSALK9-M')),
                    (('WS-C3650-24TD',
                      '03.03.03SE',
                      'cat3k_caa-universalk9'),)]
        actual = []
        for fin in sorted(os.listdir(self.test_data_dir)):
            with open(os.path.join(self.test_data_dir, fin)) as t_fin:
                actual.append(clerk.fetch_model_sw(t_fin.read()))
        self.assertEqual(actual, expected)

    def test_collate(self):
        expected = [(Device(hostname='elizabeth_cotton',
                            serial_number='ANC1111A1AB',
                            model_number='WS-C2960C-8PC-L',
                            software_version='15.0(2)SE5',
                            software_image='C2960c405-UNIVERSALK9-M'),
                     Device(hostname='howlin_wolf',
                            serial_number='ABC2222A2AB',
                            model_number='WS-C2960C-8PC-L',
                            software_version='15.0(2)SE5',
                            software_image='C2960c405-UNIVERSALK9-M'),
                     Device(hostname='lightning_hopkins',
                            serial_number='ABC3333A33A',
                            model_number='WS-C2960X-48FPD-L',
                            software_version='15.0(2)EX5',
                            software_image='C2960X-UNIVERSALK9-M'),
                     Device(hostname='lightning_hopkins',
                            serial_number='ABC4444A44A',
                            model_number='WS-C2960X-48FPD-L',
                            software_version='15.0(2)EX5',
                            software_image='C2960X-UNIVERSALK9-M'),
                     Device(hostname='lightning_hopkins',
                            serial_number='ABC5555A555',
                            model_number='WS-C2960X-24PD-L',
                            software_version='15.0(2)EX5',
                            software_image='C2960X-UNIVERSALK9-M'),
                     Device(hostname='sister_rosetta_tharpe',
                            serial_number='ABC6666A6AB',
                            model_number='WS-C3650-24TD',
                            software_version='03.03.03SE',
                            software_image='cat3k_caa-universalk9'))]
        actual = []
        actual.append(clerk.collate(self.test_data_dir))
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()

