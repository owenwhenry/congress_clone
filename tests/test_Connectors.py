import unittest
from sources.APIConnectors import cdgAPI, baseAPI, govInfoAPI


class testBaseAPI(unittest.TestCase):

    def setUp(self):
        self.api = baseAPI()

    def test_good_call(self):
        target_url = 'https://api.data.gov/congress/v2/bill'
        call_made = self.api.call(target_url)
        self.assertEqual(call_made.status_code, 200)

    def test_bad_call(self):
        target_url = 'https://api.data.gov/congresss/v2/bill'
        call_made = self.api.call(target_url)
        self.assertEqual(call_made.status_code, 404)

    def test_good_validate_time(self):
        time = '2020-01-01T00:00:00Z'
        self.assertTrue(self.api.validate_time(time))

    def test_bad_time_validate_time(self):
        time = '2020-01-01'
        self.assertFalse(self.api.validate_time(time))

    def test_bad_date_validate_time(self):
        time = '2020-01T12:10:59Z'
        self.assertFalse(self.api.validate_time(time))


class testCDGAPIConnector(unittest.TestCase):

    def setUp(self):
        self.mixin = cdgAPI()

    # Limit tests
    def test_limit_setter_good(self):
        self.mixin.limit = 10
        self.assertEqual(self.mixin.limit, 10)

    def test_limit_setter_bad(self):
        with self.assertRaises(ValueError):
            self.mixin.limit = -1

    # Offset tests
    def test_offset_setter_good(self):
        self.mixin.offset = 10
        self.assertEqual(self.mixin.offset, 10)

    def test_offset_setter_bad(self):
        with self.assertRaises(ValueError):
            self.mixin.offset = -1

    # fromDate tests
    def test_fromDateTime_setter_good(self):
        time_value = '2020-01-01T00:00:00Z'
        self.mixin.fromDateTime = time_value
        self.assertEqual(time_value, self.mixin.fromDateTime)

    def test_fromDateTime_setter_bad(self):
        time_value = '2020-01T00:00:00Z'
        with self.assertRaises(ValueError):
            self.mixin.fromDateTime = time_value

    # toDate tests
    def test_toDateTime_setter_good(self):
        time_value = '2020-01-01T00:00:00Z'
        self.mixin.toDateTime = time_value
        self.assertEqual(time_value, self.mixin.toDateTime)

    def test_toDateTime_setter_bad(self):
        time_value = '2020-01T00:00:00Z'
        with self.assertRaises(ValueError):
            self.mixin.toDateTime = time_value

    # Params
    def test_params_all(self):
        self.mixin.limit = 1
        self.mixin.offset = 2
        self.mixin.fromDateTime = '2020-01-01T00:00:00Z'
        self.mixin.toDateTime = '2020-01-01T00:00:00Z'

        self.assertEqual(self.mixin.params['limit'], 1)
        self.assertEqual(self.mixin.params['offset'], 2)
        self.assertEqual(self.mixin.params['fromDateTime'],
                         '2020-01-01T00:00:00Z')
        self.assertEqual(self.mixin.params['toDateTime'],
                         '2020-01-01T00:00:00Z')

    # create_url_from_parts
    def test_create_url_from_parts(self):
        self.mixin._url_parts = ['nomination', 116, 74]
        expected_url = 'http://api.data.gov/congress/v2/nomination/116/74/'
        returned = self.mixin.create_url_from_parts()
        self.assertEqual(expected_url, returned)

    # Congress
    def test_congress_good(self):
        cong_val = 116
        self.mixin.congress = cong_val
        self.assertEqual(cong_val, self.mixin.congress)

    def test_congress_bad(self):
        with self.assertRaises(ValueError):
            self.mixin.congress = 1

    # Pagination
    def test_pagination(self):
        """
        This should return 6 pages of bills at 20 bills a page
        Total hjres for the 116th is 110
        """
        target_url = 'https://api.data.gov/congress/v1/bill/116/hjres'
        counter = 0
        for page in self.mixin.paginate(target_url):
            counter += 1
        self.assertEqual(counter, 6)


class testGovInfoApiConnector(unittest.TestCase):

    def setUp(self):
        self.api = govInfoAPI()
        self.start_default = '2000-01-01T00:00:00Z'
        self.date_good = '2021-01-01T00:00:00Z'
        self.date_bad = '20210101T00:00:00Z'
        self.end_default = None
        self.psize_good = 100
        self.psize_bad = -1

    # lastModifiedStartDate
    def test_last_modified_start_default(self):
        self.assertEqual(self.start_default, self.api.lastModifiedStartDate)

    def test_last_modified_start_setter_good(self):
        self.api.lastModifiedStartDate = self.date_good
        self.assertEqual(self.date_good, self.api.lastModifiedStartDate)

    def test_last_modified_start_setter_bad(self):
        with self.assertRaises(ValueError):
            self.api.lastModifiedStartDate = self.date_bad

    # lastModifiedEndDate
    def test_last_modified_end_date_default(self):
        self.assertEqual(self.api.lastModifiedEndDate, self.end_default)

    def test_last_modifed_end_date_setter_good(self):
        self.api.lastModifiedEndDate = self.date_good
        self.assertEqual(self.api.lastModifiedEndDate, self.date_good)

    def test_last_modified_end_date_setter_bad(self):
        with self.assertRaises(ValueError):
            self.api.lastModifiedEndDate = self.date_bad

    # pageSize
    def test_page_size_default(self):
        self.assertEqual(self.api.page_size, 20)

    def test_page_size_setter_good(self):
        self.api.page_size = self.psize_good
        self.assertEqual(self.api.page_size, self.psize_good)

    def test_page_size_setter_bad(self):
        with self.assertRaises(ValueError):
            self.api.page_size = self.psize_bad

    # to-do: add test for pagination.
