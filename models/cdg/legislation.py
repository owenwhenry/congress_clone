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
