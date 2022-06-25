import unittest
from models.cdg.legislation import bill


class testBill(unittest.TestCase):

    def setUp(self):
        self.bill_type = 'hr'
        self.bill_num = 2546
        self.congress = 116
        self.url = 'http://api.data.gov/congress/v2/bill/116/hr/2546'
        self.bill_parts = bill(
            congress=self.congress,
            bill_type=self.bill_type,
            bill_num=self.bill_num
            )
        self.bill_url = bill(url=self.url)
        self.bill_parts.data
        self.bill_url.data

    def test_call(self):
        self.assertEqual(self.bill_url.status_code, 200)
        self.assertEqual(self.bill_parts.status_code, 200)

    def test_titles(self):
        self.assertEqual(len(self.bill_url.titles), 11)
        self.assertEqual(len(self.bill_parts.titles), 11)
        self.assertEqual(self.bill_parts.titles, self.bill_url.titles)

    def test_short_title(self):
        title_text = 'Colorado Wilderness Act of 2019'
        self.assertEqual(self.bill_url.short_title, title_text)
        self.assertEqual(self.bill_parts.short_title, title_text)

    def test_official_title(self):
        title_text = ('To designate certain lands in the State of Colorado as'
                      ' components of the National Wilderness Preservation'
                      ' System, and for other purposes.')
        self.assertEqual(self.bill_url.official_title, title_text)
        self.assertEqual(self.bill_parts.official_title, title_text)

    def test_find_title_by_tag_good(self):
        self.assertEqual
