# -*- coding: utf-8 -*-
#
# AMIVAPI schemas.py
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

from eve_sqlalchemy.decorators import registerSchema
from inspect import getmembers, isclass

from amivapi import models
from settings import ROLES


def get_domain():
    domain = {}

    for cls_name, cls in getmembers(models):
        if(isclass(cls) and
                cls.__module__ == "amivapi.models" and
                cls.__expose__ is True):
            registerSchema(cls.__tablename__)(cls)
            domain.update(cls._eve_schema)

            for field in cls.__projected_fields__:
                domain[cls.__tablename__]['datasource']['projection'].update(
                    {field: 1}
                )

            domain[cls.__tablename__]['public_methods'] = (
                cls.__public_methods__)
            domain[cls.__tablename__]['public_item_methods'] = (
                cls.__public_methods__)

            # For documentation
            domain[cls.__tablename__]['description'] = cls.__description__

            # Users should not provide _author fields
            domain[cls.__tablename__]['schema']['_author'].update(
                {'readonly': True})

    # Make it possible to retrive a user with his username (/users/name)
    domain['users'].update({
        'additional_lookup': {
            'url': 'regex(".*[\w].*")',
            'field': 'username',
        }
    })

    # Hide passwords

    domain['users']['datasource']['projection']['password'] = 0

    # Only accept email addresses for email fields
    EMAIL_REGEX = '^.+@.+$'
    domain['users']['schema']['email'].update(
        {'regex': EMAIL_REGEX})
    domain['forwardaddresses']['schema']['email'].update(
        {'regex': EMAIL_REGEX})
    domain['eventsignups']['schema']['email'].update(
        {'regex': EMAIL_REGEX})

    # Permissions: Only allow existing roles and expiry date must be in the
    # future
    domain['permissions']['schema']['role'].update(
        {'allowed': ROLES.keys()})
    domain['permissions']['schema']['expiry_date'].update(
        {'future_date': True})

    """ For confirmation: eve will not handle POST """
    domain['forwardaddresses']['resource_methods'] = ['GET']
    domain['eventsignups']['resource_methods'] = ['GET']

    domain[models.Session.__tablename__]['resource_methods'] = ['GET']

    """No Patching for files and forwardaddresses, only replacing"""
    domain[models.File.__tablename__]['item_methods'] = ['GET', 'PUT',
                                                         'DELETE']
    domain['forwardaddresses']['item_methods'] = ['GET', 'PUT', 'DELETE']

    # time_end for /events requires time_start
    domain['events']['schema']['time_end'].update({
        'dependencies': ['time_start']
    })

    # enums of sqlalchemy should directly be catched by the validator
    domain['users']['schema']['gender'].update({
        'allowed': ['male', 'female']
    })
    domain['users']['schema']['department'].update({
        'allowed': ['itet', 'mavt']
    })

    """
    Eventsignups, schema extensions including custom validation
    """
    domain['eventsignups']['schema']['event_id'].update({
        'not_patchable': True,
        'signup_requirements': True})
    domain['eventsignups']['schema']['user_id'].update({
        'not_patchable': True,
        'unique_combination': ['eventsignups', 'event_id'],
        'dependencies': ['event_id'],
        'public_check': True})
    domain['eventsignups']['schema']['email'].update({
        'not_patchable': True,
        'unique_combination': ['eventsignups', 'event_id'],
        'dependencies': ['user_id'],
        'only_anonymous': True})
    # Since the data relation is not evaluated for posting, we need to remove
    # it from the schema TODO: EXPLAIN BETTER
    del(domain['eventsignups']['schema']['email']['data_relation'])
    # Remove _email_unreg and _token from the schema since they are only
    # for internal use and should not be visible
    del(domain['eventsignups']['schema']['_email_unreg'])
    del(domain['eventsignups']['schema']['_token'])

    domain['eventsignups']['schema']['additional_fields'].update({
        'type': 'json_event_field'})

    """
    Events, schema extensions
    """
    domain['events']['schema']['additional_fields'].update({
        'type': 'json_schema'})
    domain['events']['schema']['price'].update({'min': 0})
    domain['events']['schema']['spots'].update({'min': 0})

    """
    Filetype needs to be specified as media, maybe this can be automated
    """
    domain['events']['schema'].update({
        'img_thumbnail': {'type': 'media', 'filetype': ['png', 'jpeg']},
        'img_web': {'type': 'media', 'filetype': ['png', 'jpeg']},
        'img_1920_1080': {'type': 'media', 'filetype': ['png', 'jpeg']}
    })

    domain['files']['schema'].update({
        'data': {'type': 'media', 'required': True}
    })

    domain['joboffers']['schema'].update({
        'logo': {'type': 'media', 'filetype': ['png', 'jpeg']},
        'pdf': {'type': 'media', 'filetype': ['pdf']},
    })

    """
    Locatization-revelant: Hide the mapping table
    Set title and description id from events and joboffers schema to read only
    so they can not be set manually
    Also make the localization_id and language a unique combination to avoid
    several translations in the same language
    """
    domain['translationmappings']['internal_resource'] = True
    domain['joboffers']['schema']['title_id'].update({'readonly': True})
    domain['joboffers']['schema']['description_id'].update({'readonly': True})
    domain['events']['schema']['title_id'].update({'readonly': True})
    domain['events']['schema']['description_id'].update({'readonly': True})
    domain['translations']['schema']['language'].update({
        'unique_combination': ['translations', 'localization_id']})

    return domain
