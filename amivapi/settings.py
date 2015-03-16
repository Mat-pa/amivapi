# -*- coding: utf-8 -*-
#
# AMIVAPI settings.py
# Copyright (C) 2015 AMIV an der ETH, see AUTHORS for more details
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Default settings for all environments.

These settings will be extended by additional config files in ROOT/config.
Run `python manage.py create_config` to create such a config file.
"""

from os.path import abspath, dirname, join
from datetime import timedelta

# Custom
ROOT_DIR = abspath(join(dirname(__file__), ".."))

# Flask
DEBUG = False
TESTING = False

# Flask-SQLALchemy

# Eve
ID_FIELD = "id"
AUTH_FIELD = "_author"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
BANDWIDTH_SAVER = False
RESOURCE_METHODS = ['GET', 'POST']
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']
PUBLIC_METHODS = ['GET']  # This is the only way to make / public
XML = False

# Eve, file storage options
RETURN_MEDIA_AS_BASE64_STRING = False
EXTENDED_MEDIA_INFO = ['filename', 'size', 'content_url']

# Custom Default language
DEFAULT_LANGUAGE = 'de'
SESSION_TIMEOUT = timedelta(days=365)

# Text for automatically sent mails

# First argument is role name
PERMISSION_EXPIRED_WARNMAIL_SUBJECT = (
    "Your permissions as %(role)s at AMIV are about to expire")
# First argument is name, second role, third admin email
PERMISSION_EXPIRED_WARNMAIL_TEXT = (
    "Hello %(name)s,\nYour permissions as %(role)s at AMIV will expire in 14 "
    "days. If you want to get them renewed please sent an E-Mail to "
    " %(admin_mail)s.\n\nRegards\n\nAutomatically sent by AMIV API"
)

# This is a list of which groups exist to grant permissions. It should be
# possible to change anything without breaking stuff.
ROLES = {
    'vorstand': {
        'users': {
            'GET': 1,
            'POST': 1,
            'PATCH': 1,
            'PUT': 1,
            'DELETE': 1,
        },
        'permissions': {
            'GET': 1,
            'POST': 1,
            'PATCH': 1,
            'PUT': 1,
            'DELETE': 1
        },
        'forwards': {
            'GET': 1,
            'POST': 1,
            'PATCH': 1,
            'PUT': 1,
            'DELETE': 1
        },
        'forwardusers': {
            'GET': 1,
            'POST': 1,
            'PATCH': 1,
            'PUT': 1,
            'DELETE': 1
        },
        'forwardaddresses': {
            'GET': 1,
            'POST': 1,
            'PATCH': 1,
            'PUT': 1,
            'DELETE': 1
        },
        'sessions': {
            'GET': 1,
            'DELETE': 1
        },
        'events': {
            'GET': 1,
            'POST': 1,
            'PATCH': 1,
            'PUT': 1,
            'DELETE': 1
        },
        'eventsignups': {
            'GET': 1,
            'POST': 1,
            'PATCH': 1,
            'PUT': 1,
            'DELETE': 1
        },
        'files': {
            'GET': 1,
            'POST': 1,
            'PATCH': 1,
            'PUT': 1,
            'DELETE': 1
        },
        'studydocuments': {
            'GET': 1,
            'POST': 1,
            'PATCH': 1,
            'PUT': 1,
            'DELETE': 1
        },
        'joboffers': {
            'GET': 1,
            'POST': 1,
            'PATCH': 1,
            'PUT': 1,
            'DELETE': 1
        }
    },
    'read-everything': {
        'users': {
            'GET': 1,
        },
        'permissions': {
            'GET': 1,
        },
        'forwards': {
            'GET': 1,
        },
        'forwardusers': {
            'GET': 1,
        },
        '_forwardaddresses': {
            'GET': 1,
        },
        'sessions': {
            'GET': 1,
        },
        'events': {
            'GET': 1,
        },
        'eventsignups': {
            'GET': 1,
        },
        'files': {
            'GET': 1,
        },
        'studydocuments': {
            'GET': 1,
        },
        'joboffers': {
            'GET': 1,
        }
    },
    'event-admin': {
        'events': {
            'GET': 1,
            'POST': 1,
            'PATCH': 1,
            'PUT': 1,
            'DELETE': 1
        },
        'eventsignups': {
            'GET': 1,
            'POST': 1,
            'PATCH': 1,
            'PUT': 1,
            'DELETE': 1
        }
    },
    'job-admin': {
        'files': {
            'GET': 1,
            'POST': 1,
            'PATCH': 1,
            'PUT': 1,
            'DELETE': 1
        },
        'joboffers': {
            'GET': 1,
            'POST': 1,
            'PATCH': 1,
            'PUT': 1,
            'DELETE': 1
        }
    },
    'mail-admin': {
        'forwards': {
            'GET': 1,
            'POST': 1,
            'PATCH': 1,
            'PUT': 1,
            'DELETE': 1
        },
        'forwardusers': {
            'GET': 1,
            'POST': 1,
            'PATCH': 1,
            'PUT': 1,
            'DELETE': 1
        },
        '_forwardaddresses': {
            'GET': 1,
            'POST': 1,
            'PATCH': 1,
            'PUT': 1,
            'DELETE': 1
        }
    },
    'studydocs-admin': {
        'files': {
            'GET': 1,
            'POST': 1,
            'PATCH': 1,
            'PUT': 1,
            'DELETE': 1
        },
        'studydocuments': {
            'GET': 1,
            'POST': 1,
            'PATCH': 1,
            'PUT': 1,
            'DELETE': 1
        }
    }
}
