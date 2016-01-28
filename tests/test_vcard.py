from datetime import datetime

from dateutil.tz import tzutc

from qreader.vcard import vCard
from tests.helpers import TestCase

# The things we do to increase test coverage...
# and it's a temporary module too!

__author__ = 'ewino'


class TestVCardFromText(TestCase):

    def test_format(self):
        self.assertTrue(vCard(), vCard.from_text('BEGIN:VCARD\nEND:VCARD'))
        self.assertTrue(vCard(), vCard.from_text('BEGIN:VCARD\n\nEND:VCARD'))
        self.assertRaises(ValueError, lambda: vCard.from_text('BEGIN:VCARD\nEND:ICAL'))
        self.assertRaises(ValueError, lambda: vCard.from_text('Welcome to Jamaica, Have a good day'))

    def test_weird_field(self):
        with self.assertRaises(TypeError) as cm:
            vCard.from_text('BEGIN:VCARD\nEWINO:BLA\nEND:VCARD')
        self.assertEquals(cm.exception.args[0], 'Unknown vCard field: EWINO. This implementation only supports '
                                                'basic properties')
        vCard.from_text('BEGIN:VCARD\nVERSION:4\nEND:VCARD')

    def test_date_fields(self):
        self.assertEquals(datetime(2015, 8, 28, tzinfo=tzutc()), vCard.from_text('BEGIN:VCARD\nANNIVERSARY:20150828T000000Z\nEND:VCARD').anniversary)

    def test_complex_fields(self):
        card = vCard.from_text('BEGIN:VCARD\n'
                               'TEL;TYPE=WORK,VOICE:(111) 555-1212\n'
                               'ADR;TYPE=WORK:;;100 Waters Edge;Baytown;LA;30314;United States of America\n'
                               'CATEGORIES:swimmer,biker\n'
                               'END:VCARD')
        self.assertEquals(1, len(card.phones))
        self.assertEquals(('WORK,VOICE', '(111) 555-1212'), card.phones[0])
        self.assertEquals(1, len(card.addresses))
        self.assertEquals(('WORK', '', '', '100 Waters Edge', 'Baytown', 'LA', '30314', 'United States of America'), card.addresses[0])
        self.assertEquals(2, len(card.categories))
        self.assertEquals(['swimmer', 'biker'], card.categories)
