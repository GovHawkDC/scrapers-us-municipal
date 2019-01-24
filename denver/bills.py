from legistar.bills import LegistarBillScraper, LegistarAPIBillScraper
from pupa.scrape import Bill, VoteEvent, Scraper
from pupa.utils import _make_pseudo_id
import datetime
import itertools
import pytz
import requests

def sort_actions(actions):
    action_time = 'MatterHistoryActionDate'
    action_name = 'MatterHistoryActionName'
    sorted_actions = sorted(actions,
                            key = lambda x: (x[action_time].split('T')[0],
                                             ACTION[x[action_name]]['order'],
                                             x[action_time].split('T')[1]))

    return sorted_actions

class DenverBillScraper(LegistarAPIBillScraper, Scraper):
    BASE_URL = 'http://webapi.legistar.com/v1/denver'
    BASE_WEB_URL = 'https://denver.legistar.com'
    TIMEZONE = "US/Central"

    VOTE_OPTIONS = {
                    'aye' : 'yes',
                    'present' : 'other',
                    'nay' : 'no',
                    'absent' : 'absent',
                    'excused': 'excused',
                    'abstained': 'abstain',
                    'recused': 'excused',
                    'also present': 'other',
                    'not voting': 'other',
                    'unrecorded': 'not voting'
                    }

    def session(self, action_date) :
        localize = pytz.timezone(self.TIMEZONE).localize
        return "2018-2019"
        # # 2011 Kill Bill https://chicago.legistar.com/LegislationDetail.aspx?ID=907351&GUID=6118274B-A598-4584-AA5B-ABDFA5F79506
        # if action_date <  localize(datetime.datetime(2011, 5, 4)) :
        #     return "2007"
        # # 2015 Kill Bill https://chicago.legistar.com/LegislationDetail.aspx?ID=2321351&GUID=FBA81B7C-8A33-4D6F-92A7-242B537069B3
        # elif action_date < localize(datetime.datetime(2015, 5, 6)) :
        #     return "2011"
        # else :
        #     return "2018"

    def sponsorships(self, matter_id) :
        for i, sponsor in enumerate(self.sponsors(matter_id)) :
            sponsorship = {}
            if i == 0 :
                sponsorship['primary'] = True
                sponsorship['classification'] = "Primary"
            else :
                sponsorship['primary'] = False
                sponsorship['classification'] = "Regular"

            sponsor_name = sponsor['MatterSponsorName'].strip()

            if sponsor_name.startswith(('City Clerk',)) :
                sponsorship['name'] = 'Office of the City Clerk'
                sponsorship['entity_type'] = 'organization'
            else :
                sponsorship['name'] = sponsor_name
                sponsorship['entity_type'] = 'person'

            if not sponsor_name.startswith(('Misc. Transmittal',
                                            'No Sponsor',
                                            'Dept./Agency')) :
                yield sponsorship

    def actions(self, matter_id) :
        old_action = None
        actions = self.history(matter_id)
        actions = sort_actions(actions)

        for action in actions :
            action_date = action['MatterHistoryActionDate']
            action_description = action['MatterHistoryActionName']
            responsible_org = action['MatterHistoryActionBodyName']

            action_date =  self.toTime(action_date).date()

            responsible_person = None
            if responsible_org == 'City Council' :
                responsible_org = 'Denver City Council'
            elif responsible_org == 'Office of the Mayor':
                responsible_org = 'City of Denver'
                # if action_date < datetime.date(2011, 5, 16):
                #     responsible_person = 'Daley, Richard M.'
                # else:
                #     responsible_person = 'Emanuel, Rahm'


            bill_action = {'description' : action_description,
                           'date' : action_date,
                           'organization' : {'name' : responsible_org},
                           'classification' : ACTION[action_description]['ocd'],
                           'responsible person' : responsible_person}
            if bill_action != old_action:
                old_action = bill_action
            else:
                continue

            if (action['MatterHistoryEventId'] is not None
                and action['MatterHistoryRollCallFlag'] is not None
                and action['MatterHistoryPassedFlag'] is not None) :

                # Do we want to capture vote events for voice votes?
                # Right now we are not?
                bool_result = action['MatterHistoryPassedFlag']
                result = 'pass' if bool_result else 'fail'

                votes = (result, self.votes(action['MatterHistoryId']))
            else :
                votes = (None, [])

            yield bill_action, votes

    def scrape(self, window=3) :
        n_days_ago = datetime.datetime.utcnow() - datetime.timedelta(float(window))
        for matter in self.matters(n_days_ago) :
            matter_id = matter['MatterId']

            date = matter['MatterIntroDate']
            title = matter['MatterTitle']
            identifier = matter['MatterFile']

            # If a bill has a duplicate action item that's causing the entire scrape
            # to fail, add it to the `problem_bills` array to skip it.
            # For the time being...nothing to skip!

            problem_bills = []

            if identifier in problem_bills:
                continue

            if not all((date, title, identifier)) :
                continue

            bill_session = self.session(self.toTime(date))
            bill_type = BILL_TYPES[matter['MatterTypeName']]

            if identifier.startswith('S'):
                alternate_identifiers = [identifier]
                identifier = identifier[1:]
            else:
                alternate_identifiers = []

            bill = Bill(identifier=identifier,
                        legislative_session=bill_session,
                        title=title,
                        classification=bill_type,
                        from_organization={"name":"Denver City Council"})

            legistar_web = matter['legistar_url']

            legistar_api = 'http://webapi.legistar.com/v1/denver/matters/{0}'.format(matter_id)

            bill.add_source(legistar_web, note='web')
            bill.add_source(legistar_api, note='api')

            for identifier in alternate_identifiers:
                bill.add_identifier(identifier)

            for action, vote in self.actions(matter_id) :
                responsible_person = action.pop('responsible person')
                act = bill.add_action(**action)

                if responsible_person:
                     act.add_related_entity(responsible_person,
                                            'person',
                                            entity_id = _make_pseudo_id(name=responsible_person))

                if action['description'] == 'Referred' :
                    body_name = matter['MatterBodyName']
                    if body_name != 'City Council' :
                        act.add_related_entity(body_name,
                                               'organization',
                                               entity_id = _make_pseudo_id(name=body_name))

                result, votes = vote
                if result :
                    vote_event = VoteEvent(legislative_session=bill.legislative_session,
                                           motion_text=action['description'],
                                           organization=action['organization'],
                                           classification=None,
                                           start_date=action['date'],
                                           result=result,
                                           bill=bill)

                    vote_event.add_source(legistar_web)
                    vote_event.add_source(legistar_api + '/histories')

                    for vote in votes :
                        raw_option = vote['VoteValueName'].lower()
                        clean_option = self.VOTE_OPTIONS.get(raw_option,
                                                             raw_option)
                        vote_event.vote(clean_option,
                                        vote['VotePersonName'].strip())

                    yield vote_event


            for sponsorship in self.sponsorships(matter_id) :
                bill.add_sponsorship(**sponsorship)

            for topic in self.topics(matter_id) :
                bill.add_subject(topic['MatterIndexName'].strip())

            for attachment in self.attachments(matter_id) :
                if attachment['MatterAttachmentName'] :
                    bill.add_version_link(attachment['MatterAttachmentName'],
                                          attachment['MatterAttachmentHyperlink'],
                                          media_type="application/pdf")

            bill.extras = {'local_classification' : matter['MatterTypeName']}

            # text = self.text(matter_id)

            # if text :
            #     if text['MatterTextPlain'] :
            #         bill.extras['plain_text'] = text['MatterTextPlain']

            #     if text['MatterTextRtf'] :
            #         bill.extras['rtf_text'] = text['MatterTextRtf'].replace(u'\u0000', '')

            yield bill

# http://webapi.legistar.com/v1/denver/Actions
ACTION = {
          'filed':
              {'ocd': 'filing', 'order': 0},
          'ordered published on first reading':
              {'ocd': ['introduction', 'reading-1'], 'order': 1},
          'ordered published with a future courtesy public hearing':
              {'ocd': 'introduction', 'order': 1},
          'referred':
              {'ocd': 'referral', 'order': 2},
          'adopted':
              {'ocd': 'passage', 'order': 2},
          'adopted':
              {'ocd': 'passage', 'order': 2},
          'withdrawn':
              {'ocd': 'withdrawal', 'order': 2},
          'approved by consent':
              {'ocd': 'passage', 'order': 2},
          'postponed':
              {'ocd': 'deferral', 'order': 2},
          'postponed to a date certain':
              {'ocd': 'deferral', 'order': 2},
          'approved':
              {'ocd': 'passage', 'order': 2},
          'passed' :
              {'ocd': 'passage', 'order': 2},
          'adopted en bloc' :
              {'ocd': 'passage', 'order': 2},
          'approved for filing' :
              {'ocd': 'filing', 'order': 2},
          'placed upon final consideration and do pass' :
              {'ocd': 'passage', 'order': 2},
          'ordered published with a future required public hearing' :
              {'ocd': 'introduction', 'order': 0},
          'ordered published' :
              {'ocd': 'introduction', 'order': 0},
          'amended' :
              {'ocd': 'amendment-passage', 'order': 1},
          'continued' :
              {'ocd': None, 'order': 1},
          'ordered published as amended' :
              {'ocd': 'amendment-passage', 'order': 1},
          'required public hearing on final consideration' :
              {'ocd': None, 'order': 1},
          'placed upon final consideration and do pass as amended' :
              {'ocd': ['passage', 'amendment-passage'], 'order': 1},
          'signed' :
              {'ocd': 'executive-signature', 'order': 3},
        }

# http://webapi.legistar.com/v1/denver/MatterTypes
BILL_TYPES = {'Ordinance' : 'ordinance',
              'Resolution' : 'resolution',
              'Order' : 'order',
              'Claim' : 'claim',
              'Proclamation': 'proclamation',
              'Oath of Office' : None,
              'Communication' : None,
              'Presentation': None,
              'Appointment' : 'appointment',
              'Historical': None,
              'Executive Session': None,
              'Nomination': 'nomination',
              'Announcement': None,
              'Report' : None,
              'Bill': 'bill',
              'Approved Minutes': None}

