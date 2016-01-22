import os
import shutil
import unittest

import clerk


class FindDataTest(unittest.TestCase):

    def setUp(self):
        self.test_data_dir = os.path.join(os.getcwd(), "test_data/")
        shutil.rmtree(os.path.join(
            self.test_data_dir, ".cache/"), ignore_errors=True)

    def test_find_hostname(self):
        expected = ['elizabeth_cotton',
                    'howlin_wolf',
                    'lightning_hopkins',
                    'sister_rosetta_tharpe']
        actual = []
        for fin in sorted(os.listdir(self.test_data_dir)):
            with open(os.path.join(self.test_data_dir, fin)) as t_fin:
                actual.append(clerk.find_hostname(t_fin))
        self.failUnlessEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()

