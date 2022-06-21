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


class bill(cdgAPI):
    """
    Class representing a bill in the Congress.gov API. Available properties
    include:

    Titles: official_title, short_title, titles

    Summaries: summaries, latest_summary
    """
    def __init__(self, congress=None, bill_type=None, bill_num=None,
                 url=None):
        if url is not None or (bill_type is not None and bill_num is not None
                               and congress is not None):
            super().__init__(url=url)
            self.congress = congress
            self.bill_type = bill_type
            self.bill_num = bill_num
            self._url_parts = ['bill', self.congress, self.bill_type,
                               self.bill_num]
            self._titles = None
            self._summaries = None
            self._committees = None
            self._actions = None
            self._related_bills = None
            self._cosponsors = None
            self._subjects = None
            self._amendments = None
            self._texts = None
        else:
            raise AttributeError('Please provide either a url OR a Congress, '
                                 'bill type, and bill number.')

    def fetch_all(self):
        self.get_titles()
        self.get_summaries()
        self.get_committees()
        self.get_actions()
        self.get_related_bills()
        self.get_cosponsors()
        self.get_subjects()
        self.get_amendments()
        self.get_texts()

    def get_attribute(self, source_name, obj_dict_name):
        obj = sub_list(source=self.data['bill'][source_name],
                       obj_name=obj_dict_name)
        self.data['bill'][source_name]['list'] = obj.list
        return obj

    # Titles
    def get_titles(self):
        self._titles = self.get_attribute('titles', 'titles')

    @property
    def titles(self):
        if not self._titles:
            self.get_titles()
        return self.data['bill']['titles']['list']

    @property
    def short_title(self):
        return self._find_title_by_tag(self.titles,
                                       'Short Title(s) as Introduced')

    @property
    def official_title(self):
        return self._find_title_by_tag(self.titles,
                                       'Official Title as Introduced')

    def _find_title_by_tag(self, title_json, title_type):
        if not self._data['bill']['titles']['list']:
            self.get_titles()
        try:
            if title_json is None:
                return None
            else:
                title_types_list = [item['titleType'] for item in title_json]
                title_index = title_types_list.index(title_type)
                return title_json[title_index]['title']
        except ValueError:
            return "No title(s) available."

    # Summaries
    def get_summaries(self):
        self._summaries = self.get_attribute('summaries', 'billSummaries')

    @property
    def summaries(self):
        if not self._summaries:
            self.get_summaries()
        return self.data['bill']['summaries']['list']

    @property
    def latest_summary(self):
        if not self._summaries:
            self.get_summaries()
        self.logger.debug('Accessing latest summary.')
        if self._find_latest_summary(self.summaries):
            latest = self._find_latest_summary(self.summaries)['text']
        else:
            None
        latest_stripped = strip_tags(latest) if latest else None
        return latest_stripped

    def _find_latest_summary(self, summary_json):
        if summary_json is None:
            self.logger.debug('Summary JSON provided == None, returning None')
            return None
        else:
            dates = [item['actionDate'] for item in summary_json]
            self.logger.debug('Available dates: {}'.format(dates))
            max_date = max(dates)
            self.logger.debug('Max date found: {}'.format(max_date))
            latest_summary_index = dates.index(max_date)
            latest_summary = summary_json[latest_summary_index]
            self.logger.debug('Found latest summary:{}'.format(latest_summary))
            return latest_summary

    # Committees
    def get_committees(self):
        self._committees = self.get_attribute('committees', 'billCommittees')

    @property
    def committees(self):
        if not self._committees:
            self.get_committees()
        return self._committees.list

    # Actions
    def get_actions(self):
        self.get_attribute('actions', 'actions')

    @property
    def actions(self):
        if not self._actions:
            self.get_actions()
        return self._actions.list

    # Related Bills
    def get_related_bills(self):
        self._related_bills = self.get_attribute('relatedBills',
                                                 'relatedBills')

    @property
    def related_bills(self):
        if not self._related_bills:
            self.get_related_bills()
        return self._actions.list

    # Cosponsors
    def get_cosponsors(self):
        self._cosponsors = (
            cosponsors_list(source=self.data['bill']['cosponsors'],
                            obj_name='cosponsors')
        )
        self.data['bill']['cosponsors']['list'] = self._cosponsors.list

    @property
    def cosponsors(self):
        if not self._cosponsors:
            self.get_cosponsors()
        return self._cosponsors.list

    # Subjects
    def get_subjects(self):
        self._subjects = self.get_attribute('subjects', 'billSubjects')

    @property
    def subjects(self):
        if not self._subjects:
            self.get_subjects()
        return self.data['bill']['subjects']['list']

    def get_amendments(self):
        self._amendments = self.get_attribute('amendments', 'amendments')

    @property
    def amendments(self):
        if not self._amendments:
            self.get_amendments()
        return self._amendments.list

    def get_texts(self):
        self._texts = self.get_attribute('textVersions', 'textVersions')

    @property
    def texts(self):
        if not self._texts:
            self._texts = sub_list(source=self.data['bill']['textVersions'],
                                   obj_name='textVersions')
            self.data['bill']['textVersions']['list'] = self._texts.list
        return self._texts.list


class amendment(cdgAPI):
    def __init__(self, url=None, congress=None, amdmt_num=None,
                 amdmt_type=None):
        if url is not None or (congress is not None and amdmt_num is not None
                               and amdmt_type is not None):
            super().__init__(url=url)
            self.congress = congress
            self.amdmt_num = amdmt_num
            self.amdmt_type = amdmt_type
            self._url_parts = ['amendment', self.congress, self.amdmt_type,
                               self.amdmt_num]
        else:
            raise AttributeError(('Please provide either a URL OR a congress, '
                                  'amdmt_num, and amdmt_type'))


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
