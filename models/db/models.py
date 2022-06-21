from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean
from database import Base


class Bill(Base):
    __tablename__ = 'bill'
    bill_id = Column(Integer, primary_key=True)
    congress = Column(Integer, nullable=False)
    bill_number = Column(String(5), nullable=False)
    bill_type = Column(String(7), nullable=False)
    introduced_date = Column(Date, nullable=False)
    ext_create_date = Column(DateTime, nullable=False)
    ext_update_date = Column(DateTime, nullable=False)
    create_date = Column(DateTime)
    update_date = Column(DateTime)

    def __init__(self, congress=None, bill_number=None, bill_type=None,
                 introduced=None,  ext_create=None, ext_update=None):
        self.congress = congress
        self.bill_number = bill_number
        self.bill_type = bill_type
        self.introduced_date = introduced
        self.ext_create_date = ext_create
        self.ext_update_date = ext_update

    def __repr__(self):
        return '{} {} {}'.format(self.congress, self.bill_type,
                                 self.bill_number)


class Vote(Base):
    __tablename__ = 'vote'
    vote_id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, foreign_key=True)
    roll_number = Column(Integer, nullable=False)
    url = Column(String(255), nullable=False)
    chamber = Column(String(6), nullable=False)
    congress = Column(Integer, nullable=False)
    session = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False)

    def __init__(self, bill_id=None, roll_num=None, url=None, chamber=None,
                 congress=None, session=None, date=None):
        self.bill_id = None
        self.roll_number = roll_num
        self.url = url
        self.chamber = chamber
        self.congress = congress
        self.session = session
        self.date = date

    def __repr__(self):
        return '{} {} Roll Call No. {}'.format(self.congress, self.chamber,
                                               self.roll_number)


class BillCommittee(Base):
    __tablename__ = 'bill_committee'
    bill_committee_id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, foreign_key=True)
    committee_id = Column(Integer, foreign_key=True)
    activity_name = Column(String(255), nullable=False)
    activity_date = Column(Date, nullable=False)
    create_date = Column(Date)
    update_date = Column(Date)

    def __init__(self, bill_id=None, committee_id=None, activity_name=None,
                 activity_date=None, create_date=None, update_date=None):
        self.bill_id = bill_id,
        self.committee_id = committee_id
        self.activity_name = activity_name
        self.activity_date = activity_date
        self.create_date = create_date
        self.update_date = update_date

    def __repr__(self):
        return 'BillCommittee ID {}'.format(self.bill_committee_id)


class Committee(Base):
    __tablename__ = 'committee'
    committee_id = Column(Integer, primary_key=True)
    committee_code = Column(String(7), nullable=False)
    parent_committee_code = Column(String(7), nullable=False)
    name = Column(String(1024), nullable=False)
    comm_type = Column(String(10), nullable=False)
    ext_create_date = Column(Date, nullable=False)
    ext_update_date = Column(Date, nullable=False)
    is_current = Column(Boolean)

    def __init__(self, committee_code=None, parent_committee_code=None,
                 name=None, comm_type=None, ext_create_date=None,
                 ext_update_date=None, is_current=None):
        self.committee_code = committee_code
        self.parent_committee_code = parent_committee_code
        self.name = name
        self.comm_type = comm_type
        self.ext_create_date = ext_create_date
        self.ext_update_date = ext_update_date
        self.is_current = is_current

    def __repr__(self):
        return '{}'.format(self.name)


class Related(Base):
    __tablename__ = 'related'
    related_id = Column(Integer, primary_key=True)
    bill_id_1 = Column(Integer, foreign_key=True)
    bill_id_2 = Column(Integer, foreign_key=True)
    relationship_type = Column(String(50), nullable=False)
    identified_by = Column(String(10), nullable=False)

    def __init__(self, bill_id_1=None, bill_id_2=None, relationship_type=None,
                 identified_by=None):
        self.bill_id_1 = bill_id_1
        self.bill_id_2 = bill_id_2
        self.relationship_type = relationship_type
        self.identified_by = identified_by


class Actions(Base):
    __tablename__ = 'actions'
    action_id = Column(Integer, primary_key=True)
    committee_id = Column(Integer, foreign_key=True)
    action_date = Column(Date)
    action_text = Column(String(4000))
    action_type = Column(String(100))
    action_code = Column(String(10))
    source_system_code = Column(Integer)
    source_system_name = Column(String(15))

    def __init__(self, action_date=None, action_text=None, action_type=None,
                 action_code=None, source_system_code=None,
                 source_system_name=None):
        self.action_date = action_date
        self.action_text = action_text
        self.action_type = action_type
        self.action_code = action_code
        self.source_system_code = source_system_code
        self.source_system_name = source_system_name


class Sponsorship(Base):
    __tablename__ = 'sponsorship'
    sponsorship_id = Column(Integer, primary_key=True)
    bioguide_id = Column(String(7), nullable=False)
    full_name = Column(String(255))
    first_name = Column(String(255))
    middle_name = Column(String(255))
    last_name = Column(String(255))
    party = Column(String(1))
    state = Column(String(2))
    district = Column(String(3))
    sponsorship_date = Column(Date)
    is_original_cosponsor = Column(Boolean)
    sponsorship_withdrawn_date = Column(Date)

    def __init__(self, bioguide_id=None, full_name=None, first_name=None,
                 middle_name=None, last_name=None, party=None, state=None,
                 district=None, sponsorship_date=None,
                 is_original_cosponsor=None, sponsorship_withdrawn_date=None):
        self.bioguide_id = bioguide_id
        self.full_name = full_name
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.party = party
        self.state = state
        self.district = district
        self.sponsorship_date = sponsorship_date
        self.is_original_cosponsor = is_original_cosponsor
        self.sponsorship_withdrawn_date = sponsorship_withdrawn_date


class Subjects(Base):
    __tablename__ = 'subject'


class PolicyArea(Base):
    __tablename__ = 'policy_area'


class Titles(Base):
    __tablename__ = 'title'


class Amendment(Base):
    __tablename__ = 'amendment'
