import datetime
import unittest

from match_service import utils

TEST_NON_OVERLAPPING_INTERVALS = [
    [datetime.date(2014, 7, 20), datetime.date(2018, 10, 18)],
    [datetime.date(2019, 1, 8), datetime.date(2020, 9, 13)],
    [datetime.date(2021, 12, 8), datetime.date(2023, 4, 20)],
]

TEST_OVERLAPPING_INTERVALS = [
    [datetime.date(2014, 7, 20), datetime.date(2018, 10, 18)],
    [datetime.date(2018, 10, 18), datetime.date(2020, 9, 13)],
    [datetime.date(2020, 9, 13), datetime.date(2023, 4, 20)],
]

TEST_PARTIALLY_OVERLAPPING_INTERVALS = [
    [datetime.date(2014, 7, 20), datetime.date(2018, 10, 18)],
    [datetime.date(2019, 10, 18), datetime.date(2020, 9, 13)],
    [datetime.date(2020, 9, 13), datetime.date(2023, 4, 20)],
]

TEST_NESTED_INTERVALS = [
    [datetime.date(1999, 7, 20), datetime.date(2022, 10, 18)],
    [datetime.date(2013, 10, 18), datetime.date(2018, 9, 13)],
    [datetime.date(2014, 9, 13), datetime.date(2017, 4, 20)],
    [datetime.date(2015, 6, 15), datetime.date(2016, 7, 22)],
]


class TestUtils(unittest.TestCase):
    def test_merge_non_overlapping_intervals(self):
        self.assertEqual(
            utils.merge_intervals(TEST_NON_OVERLAPPING_INTERVALS),
            TEST_NON_OVERLAPPING_INTERVALS,
        )

    def test_merge_overlapping_intervals(self):
        self.assertEqual(
            utils.merge_intervals(TEST_OVERLAPPING_INTERVALS),
            [[datetime.date(2014, 7, 20), datetime.date(2023, 4, 20)]],
        )

    def test_merge_partially_overlapping_intervals(self):
        self.assertEqual(
            utils.merge_intervals(TEST_PARTIALLY_OVERLAPPING_INTERVALS),
            [
                [datetime.date(2014, 7, 20), datetime.date(2018, 10, 18)],
                [datetime.date(2019, 10, 18), datetime.date(2023, 4, 20)],
            ],
        )

    def test_merge_nested_intervals(self):
        self.assertEqual(
            utils.merge_intervals(TEST_NESTED_INTERVALS),
            [[datetime.date(1999, 7, 20), datetime.date(2022, 10, 18)]],
        )


if __name__ == '__main__':
    unittest.main()
