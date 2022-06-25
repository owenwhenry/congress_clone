"""
Last updated 3/18/2021

Classes in this module are meant to represent objects that appear in the CDG
API and to help serve as guard-rails for people accessing it.

Certain objects may contain additional features or functions designed to
facilitate access to their data. See each object's help for more information
on what functions are available for that specific object.

Available objects include:
    amendment
    bill
    committee
    committeeReport
    member
    nomination
"""
from APIConnectors import cdgAPI
from io import StringIO
from html.parser import HTMLParser


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class sub_list(cdgAPI):
    """
    Represents a nested list in the Congress.gov API. Used when the API wants
    you to make a secondary call to retrieve information. You can either use
    <object name>.list to get all the sub items, or you can get the items
    directly from the function by calling <object_name>.get_list()
    """
    def __init__(self, source=None, obj_name=None):
        super().__init__(url=source['url'])
        self.count = source['count'] if 'count' in source else None
        self.name = obj_name
        self._list = None

    @property
    def list(self):
        if self.count is None:
            return None
        elif not self._list:
            self._list = list()
            for item in self.get_list():
                self._list.append(item)
        return self._list

    def get_list(self):
        """
        Generator function that will make the call to the additional endpoint
        and, if neccessary, paginate the results. Yields list items.
        """
        self.logger.debug('Getting sub list of objects')
        if self.count > self.limit:
            self.logger.debug(('Result count of {} greater than page size of '
                               '{}, paginating.'.format(self.count,
                                                        self.limit)))
            for result in self.paginate(self.url):
                for item in result[self.name]:
                    self.logger.debug('Yielding {}'.format(item))
                    yield item
        else:
            obj_call = self.get()
            for item in obj_call[self.name]:
                self.logger.debug('Yielding {}'.format(item))
                yield item


class cosponsors_list(sub_list):

    def __init__(self, source=None, obj_name=None):
        super().__init__(source=source['url'], obj_name=obj_name)
        self.count = source['totalCount'] if 'totalCount' in source else None
        self._list = None


class object_list(cdgAPI):
    """
    In cases where there's more than 1, and potentially many, types of related
    objects, the Congress.gov API uses a pattern where it gives you a URL and
    a count of objects, then invites you to go fetch the list for yourself. The
    object list represents this pattern for the purposes of extracting the data
    for each of these related objects. Deprecated in favor of sub_list.
    """
    def __init__(self, source=None, obj_class=None):
        super().__init__(url=source['url'])
        self.count = source['count'] if source['count'] else None
        self._obj_class = obj_class
        self.name = obj_class.name
        self._list = None
        self._obj_list = None

    @property
    def list(self):
        if self.count == 0:
            return None
        elif not self._list:
            self._list = self.get_list()
        return self._list

    @property
    def obj_list(self):
        if not self._obj_list:
            self._obj_list = [self._obj_class(item) for item in self.list]
        else:
            return self._obj_list

    def get_list(self):
        self.logger.debug('Getting sub list of objects')
        obj_list = list()
        if self.count > self.limit:
            self.logger.debug(('Result count of {} greater than page size of '
                               '{}, paginating.').format(self.count,
                                                         self.limit))
            for result in self.paginate(self.url):
                obj_list.append(result[self.name])
        else:
            obj_call = self.get()
            obj_list.append(obj_call[self.name])
        return obj_list


class committee(cdgAPI):
    def __init__(self, chamber=None, committee_id=None, url=None):
        if url is not None or (chamber is not None
                               and committee_id is not None):
            super().__init__(url=url)
            self.chamber = chamber
            self.committee_id = committee_id
            self._url_parts = ['committee', self.committee_id]
        else:
            raise AttributeError('Please provide either a URL OR a chamber and'
                                 ' committee_id_num')


class committeeReport(cdgAPI):
    def __init__(self, url=None, congress=None, report_type=None,
                 report_num=None):
        if url is None or (congress is None and
                           report_type is None
                           and report_num is None):
            super().__init__(url=url)
            self.congress = congress
            self.report_type = report_type
            self.report_num = report_num
            self._url_parts = ['committeeReport', self.congress,
                               self.report_type, self.report_num]
        else:
            raise AttributeError('Please provide either a URL OR a congress, '
                                 'report_type, and report_num')


class actions():
    """
    Represents action objects and data in the Congress.gov API. You can either
    access the raw data and deal with it as nested json, or access properties
    of the action by typing <object name>.<property>. Valid properties include:

        action_code, action_date, action_type, committee, committee_code,
        committee_url, data, links, source_system_code, source_system_id,
        source_system_name, text
    """
    def __init__(self, data=None):
        self._data = data

    @property
    def data(self):
        return self._data

    @property
    def action_date(self):
        return self._data['actionDate'] if self._data['actionDate'] else None

    @property
    def links(self):
        if self._data['links']:
            if len(self._data['links']) > 0:
                return self._data['links']
        else:
            return None

    @property
    def text(self):
        return self._data['text'] if self._data['text'] else None

    @property
    def action_type(self):
        return self._data['type'] if self._data['type'] else None

    @property
    def action_code(self):
        return self._data['actionCode'] if self._data['actionCode'] else None

    @property
    def source_system_name(self):
        if self._data['sourceSystem']['name']:
            return self._data['sourceSystem']['name']
        else:
            return None

    @property
    def source_system_code(self):
        if self._data['sourceSystem']['code']:
            return self._data['sourceSystem']['code']
        else:
            return None

    @property
    def source_system_id(self):
        if self._data['sourceSystem']['systemCode']:
            return self._data['sourceSystem']['systemCode']
        else:
            return None

    @property
    def committee(self):
        if self._data['committee']['name']:
            return self._data['committee']['name']
        else:
            None

    @property
    def committee_code(self):
        if self._data['committee']['systemCode']:
            return self._data['committee']['systemCode']
        else:
            None

    @property
    def committee_url(self):
        if self._data['committee']['url']:
            return self._data['committee']['url']
        else:
            None
