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
