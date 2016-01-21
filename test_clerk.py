import os

import clerk

TEST_DATA_DIR = os.path.join(os.getcwd(), "test_data/")


def test_find_hostname():
    expected = ['elizabeth_cotton',
                'howlin_wolf',
                'lightning_hopkins',
                'sister_rosetta_tharpe']
    actual = []
    for fin in sorted(os.listdir(TEST_DATA_DIR)):
        with open(os.path.join(TEST_DATA_DIR, fin)) as test_data_file:
            actual.append(clerk.find_hostname(test_data_file))
    assert actual == expected

