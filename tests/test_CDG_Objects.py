import unittest
from sources import cdgAPIObjects


class testBill(unittest.TestCase):

    def setUp(self):
        self.bill_type = 'hr'
        self.bill_num = 2546
        self.congress = 116
        self.url = 'http://api.data.gov/congress/v2/bill/116/hr/2546'
        self.bill_parts = cdgAPIObjects.bill(congress=self.congress,
                                             bill_type=self.bill_type,
                                             bill_num=self.bill_num)
        self.bill_url = cdgAPIObjects.bill(url=self.url)
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


class testAction(unittest.TestCase):

    def setUp(self):
        self.data = {
            "actionCode": "S05750",
            "actionDate": "2019-02-14",
            "committee": {
                "name": "Banking, Housing, and Urban Affairs Committee",
                "systemCode": "ssbk00",
                "url": ("https://api.data.gov/congress/v2/committee/senate/"
                        "ssbk00?format=json")
            },
            "links": list(),
            "text": ("Committee on Banking, Housing, and Urban Affairs."
                     " Hearings held. Hearings printed: S.Hrg. 116-1."),
            "type": "Committee"
        }
        self.action = cdgAPIObjects.actions(self.data)

    def test_code(self):
        self.assertEqual(self.data['actionCode'], self.action.action_code)

    def test_date(self):
        self.assertEqual(self.data['actionDate'], self.action.action_date)

    def test_links(self):
        self.assertEqual(self.data['links'], self.action.links)

    def test_text(self):
        self.assertEqual(self.data['text'], self.action.text)

    def test_type(self):
        self.assertEqual(self.data['type'], self.action.action_type)

    def test_committee(self):
        self.assertEqual(self.data['committee']['name'], self.action.committee)

    def test_committee_url(self):
        self.assertEqual(self.data['committee']['url'],
                         self.action.committee_url)

    def test_committee_code(self):
        self.assertEqual(self.data['committee']['systemCode'],
                         self.action.committee_code)


class testObjectList(unittest.TestCase):

    def setUp(self):
        pass
