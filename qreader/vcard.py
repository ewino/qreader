from datetime import datetime
import re
import dateutil.parser
import six

__author__ = 'ewino'


# A very small vCard parsing implementation, because vobject's looks quite very bloated.
# Will probably be replaced by vobject or a lighter library (if I find one)


class vCard(object):

    def __init__(self):
        self.addresses = []
        self.agent = None
        self.anniversary = None
        self.bday = None
        self.categories = []
        self.emails = []
        self.formatted_name = None
        self.gender = None
        self.geo = None
        self.impp = []
        self.key = None
        self.address_labels = []
        self.lang = None
        self.logo = None
        self.name = None
        self.note = None
        self.nickname = None
        self.org = None
        self.photo = None
        self.rev = None
        self.role = None
        self.phones = []
        self.tz = None

    @classmethod
    def from_text(cls, txt):
        lines = txt.splitlines()
        """ :type: list[str] """
        if lines[0] == 'BEGIN:VCARD' and lines[-1] == 'END:VCARD':
            lines = lines[1:-1]
        else:
            raise ValueError('Not a valid vCard format')

        key_field_map = {
            'ADR': 'addresses',
            'AGENT': 'agent',
            'ANNIVERSARY': ('anniversary', datetime),
            'BDAY': ('bday', datetime),
            'CATEGORIES': ('categories', list),
            'EMAIL': 'emails',
            'FN': 'formatted_name',
            'GENDER': 'gender',
            'GEO': 'geo',
            'IMPP': 'impp',
            'KEY': 'key',
            'LABEL': 'address_labels',
            'LANG': 'lang',
            'LOGO': 'logo',
            'N': 'name',
            'NICKNAME': 'nickname',
            'NOTE': 'note',
            'ORG': 'org',
            'PHOTO': 'photo',
            'REV': ('rev', datetime),
            'TEL': 'phones',
            'ROLE': 'role',
            'TZ': 'tz',
        }
        ignore_fields = {'VERSION'}

        card = cls()

        for line in lines:
            if not line.strip():
                continue
            key, val = line.split(':', 1)
            if key in ignore_fields:
                continue
            if ';' in key:
                key, extra = re.findall('^(\w+);(?:\w+=)?(.+)$', key)[0]
                val = '%s;%s' % (extra, val)
            field = key_field_map.get(key)
            if not field:
                raise TypeError('Unknown vCard field: %s. This implementation only supports basic properties' % key)
            if isinstance(field, tuple):
                field, tpe = field
                if tpe == datetime:
                    val = dateutil.parser.parse(val)
                elif tpe == list:
                    val = val.split(',')
            if isinstance(val, six.string_types) and ';' in val:
                val = tuple(val.split(';'))

            if isinstance(getattr(card, field), list):
                prop = getattr(card, field)
                if isinstance(val, list):
                    prop.extend(val)
                else:
                    prop.append(val)
            else:
                setattr(card, field, val)
        return card
