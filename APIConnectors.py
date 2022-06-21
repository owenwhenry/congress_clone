"""
Last updated 3/18/2021

Functions in this module are connectors to various API's. At the moment only
the CDG API is accounted for, future plans include the govInfo API and
House, Senate API's
"""
import requests as req
import re
import logging
from settings import MIN_CONGRESS, CURRENT_CONGRESS
from keys import API_KEY


class baseAPI:
    """
    Base class used for handling common tasks within an API, such as
    pagination, authentication, etc.

    This is designed to be re-usable for both the Congress.gov API and the
    govinfo API, so only the stuff that's common to both goes in this class.
    You probably shouldn't be using this class at all unless you know what
    you're doing.

    Anything that's specific to the functionality of either govInfo or CDG goes
    in the corresponding class.

    Functions
         - call - makes an API call using the object's params dictionary.
           Returns requests response object.

         - paginate - generator that yields the entirety of a call's response
           object, then gets the next page and yields that and so on until
           there are no more pages of data.

         - validate_time - makes sure a timestamp is in a valid ISO8601 format.
           This is used as part of the setter methods for timestamp params.
    """
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self._api_key = API_KEY
        self._offset = 0
        self._params = dict()
        self._data = None
        self._url = None
        self._base_url = None
        self._url_parts = list()
        self._congress = None
        self._min_congress = 0
        self._max_congress = CURRENT_CONGRESS
        self.status_code = None

    @property
    def congress(self):
        return self._congress

    @congress.setter
    def congress(self, new_congress_value):
        if new_congress_value is None:
            self._congress is None
        elif (new_congress_value >= self._min_congress
              and new_congress_value <= self._max_congress):
            self._congress = new_congress_value
        else:
            raise ValueError(('Congress value is not valid for this object'
                              'type, select a value between %s and %s' % (
                               self._min_congress, self._max_congress)))

    def create_url_from_parts(self):
        """
        Creates an API url from the parts provided, assuming they exist.

        If they don't exist, raises an error.
        """
        url_string = self._base_url
        self.logger.debug(('Formatting url based on'
                           ' parts: {}'.format(self._url_parts)))
        for part in self._url_parts:
            if part is None:
                raise AttributeError('Missing the url part %s' % part)
            else:
                str_part = str(part)
                url_string += str_part
                url_string += '/'
        self.logger.debug('Formatted URL as {}'.format(url_string))
        return url_string

    def get(self):
        """
        Method for fetching data from the API and returning it as JSON.

        If you want the full request object, try call() instead.
        """
        object_raw = self.call(self.url)
        object_json = object_raw.json()
        return object_json

    # url
    @property
    def url(self):
        return self._url if self._url else self.create_url_from_parts()

    @property
    def data(self):
        if not self._data:
            self._data = self.get()
        return self._data

    def call(self, url):
        """
        Makes an API call and returns the full request object.

        Raises errors if a non-200 status is
        """
        self.logger.debug('Making call with %s' % url)
        data = req.get(url, params=self.params)
        self.status_code = data.status_code
        self.logger.debug('Call made, returning response')
        if data.status_code != 200:
            self.logger.warning('Call returned non-200'
                                ' status of %s' % data.status_code)
        return data

    def validate_time(self, timestring):
        """
        Helper function that checks whether a timestamp is in an ISO8601 format

        Returns TRUE if it is, FALSE if it isn't.
        """
        valid_format = '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z'
        return bool(re.match(valid_format, timestring))

    @property
    def api_key(self):
        """
        Getter method for the private api_key variable
        """
        return self._api_key

    @property
    def params(self):
        """
        Getter method for the params. Note that this builds the params based on
        the current state of the object, so you have to be careful from one
        call to another.
        """
        params_dict = self._params
        if self.api_key:
            params_dict['api_key'] = self.api_key
        if self.offset:
            params_dict['offset'] = self.offset
        return params_dict

    # offset
    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, new_offset):
        """
        Setter for offset. Checks to make sure the value being passed is a
        valid integer to help prevent weird behavior from the API.
        """
        if type(new_offset) == int and new_offset > 0:
            self._offset = new_offset
        else:
            raise ValueError('Offset must be an integer greater than 0')

    @offset.deleter
    def offset(self):
        """
        We always need an offset parameter, so deleting it just sets it back
        to 0
        """
        self._offset = 0


class govInfoAPI(baseAPI):

    def __init__(self, url=None):
        super().__init__()
        self._base_url = 'https://api.govinfo.gov/'
        self._page_size = 20
        self._fromDateTime = None
        self._toDateTime = None
        self._params = {'api_key': self._api_key}
        self._congress = None
        self._max_congress = CURRENT_CONGRESS
        self._url = url

    # limit
    @property
    def page_size(self):
        return self._page_size

    @page_size.setter
    def page_size(self, new_limit):
        """
        Setter method, makes sure the limit is a valid integer greater than 0
        """
        if type(new_limit) == int and new_limit > 0 and new_limit < 1000:
            self._page_size = new_limit
        else:
            raise ValueError('{} is invalid, provide an integer between 0'
                             ' and 1000'.format(new_limit))

    @page_size.deleter
    def page_size(self):
        self._page_size = 20

    # lastModifiedStartDate
    @property
    def lastModifiedStartDate(self):
        if not self._fromDateTime:
            self._fromDateTime = '2000-01-01T00:00:00Z'
        return self._fromDateTime

    @lastModifiedStartDate.setter
    def lastModifiedStartDate(self, time_string):
        """
        Makes sure the time is a valid ISO8601 timestamp with validate_time
        """
        if self.validate_time(time_string) is True:
            self._fromDateTime = time_string
        else:
            raise ValueError('%s is not a valid datetime in format ')

    @lastModifiedStartDate.deleter
    def lastModifiedStartDate(self, time_string):
        self._fromDateTime = None

    # lastModifiedEndDate
    @property
    def lastModifiedEndDate(self):
        return self._toDateTime

    @lastModifiedEndDate.setter
    def lastModifiedEndDate(self, time_string):
        """
        Makes sure the time is a valid ISO8601 timestamp with validate_time
        """
        if self.validate_time(time_string) is True:
            self._toDateTime = time_string
        else:
            raise ValueError('Time does not match format %Y-%m-%dT%h:%m:%sZ')

    @lastModifiedEndDate.deleter
    def lastModifiedEndDate(self, time_string):
        self._toDateTime = None

    def paginate(self, url):
        """
        Generator that makes the initial call to a URL then paginates through
        the rest of the results.

        Returns the entire response, one page at a time then clears the params.
        """
        target_url = url
        while target_url:
            data = self.call(target_url)
            json_data = data.json()
            yield json_data
            if 'nextPage' in json_data.keys():
                target_url = json_data['nextPage']
            else:
                target_url = None


class cdgAPI(baseAPI):
    """
    Base class used for handling common tasks within an API, such as
    pagination, authentication, etc.

    This is designed to be re-usable for both the Congress.gov API and the
    govinfo API, so only the stuff that's common to both goes in this class.
    You probably shouldn't be using this class at all unless you know what
    you're doing.

    Anything that's specific to the functionality of either govInfo or CDG goes
    in the corresponding class.

    Functions

        call - makes an API call using the object's params dictionary. Returns
        a requests response object.

        paginate - generator that yields the entirety of a call's response
        object, then gets the next page and yields that and so on until there
        are no more pages of data. Use this for dealing with multiple pages of
        results.

        validate_time - makes sure a timestamp is in a valid ISO8601 format.
        This is used as part of the setter methods for timestamp params.
    """

    def __init__(self, url=None):
        super().__init__()
        self._base_url = 'http://api.data.gov/congress/v2/'
        self._limit = 20
        self._fromDateTime = None
        self._toDateTime = None
        self._params = {'api_key': self._api_key}
        self._congress = None
        self._max_congress = CURRENT_CONGRESS
        self._min_congress = MIN_CONGRESS
        self._url = url

    # limit
    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, new_limit):
        """
        Setter method, makes sure the limit is a valid integer greater than 0
        """
        if type(new_limit) == int and new_limit > 0 and new_limit < 1000:
            self._limit = new_limit
        else:
            raise ValueError('{} is invalid, provide an integer between 0'
                             ' and 1000'.format(new_limit))

    @limit.deleter
    def limit(self):
        self._limit = 0

    # fromDateTime
    @property
    def fromDateTime(self):
        return self._fromDateTime

    @fromDateTime.setter
    def fromDateTime(self, time_string):
        """
        Makes sure the time is a valid ISO8601 timestamp with validate_time
        """
        if self.validate_time(time_string) is True:
            self._fromDateTime = time_string
        else:
            raise ValueError('%s is not a valid datetime in format ')

    @fromDateTime.deleter
    def fromDateTime(self, time_string):
        self._fromDateTime = None

    # toDateTime
    @property
    def toDateTime(self):
        return self._toDateTime

    @toDateTime.setter
    def toDateTime(self, time_string):
        """
        Makes sure the time is a valid ISO8601 timestamp with validate_time
        """
        if self.validate_time(time_string) is True:
            self._toDateTime = time_string
        else:
            raise ValueError('Time does not match format %Y-%m-%dT%h:%m:%sZ')

    @toDateTime.deleter
    def toDateTime(self, time_string):
        self._toDateTime = None

    # Params
    @property
    def params(self):
        """
        Getter method for the params. Note that this builds the params based on
        the current state of the object, so you have to be careful from one
        call to another.
        """
        params_dict = self._params
        if self.limit:
            params_dict['limit'] = self.limit
        if self.offset:
            params_dict['offset'] = self.offset
        if self.fromDateTime:
            params_dict['fromDateTime'] = self.fromDateTime
        if self.toDateTime:
            params_dict['toDateTime'] = self.toDateTime
        return params_dict

    def paginate(self, url):
        """
        Generator that makes the initial call to a URL then paginates through
        the rest of the results.

        Returns the entire response, one page at a time then clears the params.
        """
        target_url = url
        while target_url:
            data = self.call(target_url)
            json_data = data.json()
            yield json_data
            if 'next' in json_data['pagination'].keys():
                target_url = json_data['pagination']['next']
            else:
                target_url = None
