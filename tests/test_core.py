import unittest
from models.cdg.core import actions


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
        self.action = actions(self.data)

    def test_code(self):
        self.assertEqual(self.data['actionCode'], self.action.action_code)

    def test_date(self):
        self.assertEqual(self.data['actionDate'], self.action.action_date)

    def test_links(self):
        self.assertEqual(None, self.action.links)

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
