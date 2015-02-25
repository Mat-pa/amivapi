from flask import current_app as app
from flask import abort, g
from eve.utils import debug_error_message
from eve.validation import ValidationError
from eve.methods.common import payload
# from amivapi.validation import ValidatorAMIV

import datetime as dt
import json

from amivapi import models, confirm

resources_hooked = ['forwardusers', 'events', 'eventsignups', 'permissions']


def pre_insert_callback(resource, items):
    """
    general function to call the custom logic validation"""
    if resource in resources_hooked:
        for doc in items:
            eval("check_%s" % resource)(doc)


def pre_update_callback(resource, updates, original):
    """
    general function to call the custom logic validation"""
    if resource in resources_hooked:
        data = original.copy()
        data.update(updates)
        eval("check_%s" % resource)(data)


""" /forwardusers """


def check_forwardusers(data):
    db = app.data.driver.session

    forwardid = data.get('forward_id')
    forward = db.query(models.Forward).get(forwardid)

    """ Users may only self enroll for public forwards """
    if not forward.is_public and not g.resource_admin_access \
            and not g.logged_in_user == forward.owner_id:
        abort(403, description=debug_error_message(
            'You are not allowed to self enroll for this forward'
        ))

""" /signups """


def check_eventsignups(data):
    db = app.data.driver.session

    eventid = data.get('event_id')
    event = db.query(models.Event).get(eventid)

    """check for available places"""
    if event.spots > 0:
        goneSpots = db.query(models.EventSignup).filter(
            models.EventSignup.event_id == eventid
        ).count()
        if goneSpots >= event.spots:
            abort(422, description=debug_error_message(
                'There are no spots left for event %d' % eventid
            ))
    if event.spots == -1:
        abort(422, description=(
            'Event %d does not offer a signup.' % eventid
        ))

    """check for correct signup time"""
    now = dt.datetime.now()
    if event.spots >= 0:
        if now < event.time_register_start:
            abort(422, description=(
                'The signup for event %d is not open yet.' % eventid
            ))
        if now > event.time_register_end:
            abort(422, description=(
                'The signup for event %d is closed.' % eventid
            ))

    if data.get('user_id') == -1:
        if event.is_public is False:
            abort(422, description=debug_error_message(
                'The event is only open for registered users.'
            ))
        email = data.get('email')
        if email is None:
            abort(422, description=debug_error_message(
                'You need to provide an email-address or a valid user_id'
            ))
        alreadysignedup = db.query(models.EventSignup).filter(
            models.EventSignup.event_id == eventid,
            models.EventSignup.user_id == -1,
            models.EventSignup.email == email
        ).first() is not None
    else:
        userid = data.get('user_id')
        alreadysignedup = db.query(models.EventSignup).filter(
            models.EventSignup.event_id == eventid,
            models.EventSignup.user_id == userid
        ).first() is not None
        email = data.get('email')
        if email is None:
            data['email'] = db.query(models.User).get(userid).email
    if alreadysignedup:
        abort(422, description=debug_error_message(
            'You are already signed up for this event, try to use PATCH'
        ))
    if 'extra_data' in data:
        data['extra_data'] = json.dumps(data.get('extra_data'))


def update_signups_schema(data):
    """
    validate the schema of extra_data"""
    db = app.data.driver.session
    eventid = data.get('event_id')
    event = db.query(models.Event).get(eventid)
    if event is not None:
        extraSchema = event.additional_fields
        if extraSchema is not None:
            resource_def = app.config['DOMAIN']['eventsignups']
            resource_def['schema'].update({
                'extra_data': {
                    'type': 'dict',
                    'schema': json.loads(extraSchema),
                    'required': True,
                }
            })
            if data.get('extra_data') is None:
                abort(422, description=debug_error_message(
                    'event %d requires extra data: %s' % (eventid, extraSchema)
                ))
        else:
            resource_def = app.config['DOMAIN']['eventsignups']
            resource_def['schema'].update({
                'extra_data': {
                    'required': False,
                }
            })


def pre_signups_post_callback(request):
    update_signups_schema(payload())


def signups_confirm_anonymous(items):
    """
    hook to confirm external signups"""
    for doc in items:
        if doc['user_id'] == -1:
            if not confirm.confirm_actions(
                ressource='eventsignups',
                method='POST',
                doc=doc,
                email_field='email',
            ):
                items.remove(doc)


def post_signups_post_callback(request, payload_arg):
    """
    informs the user that an email with confirmation token was sent

    payload_arg only needs the '_arg' because python gets confused with the
    function 'payload()' otherwise
    """
    data = payload()
    if data.get('user_id') == -1:
        confirm.return_status(payload_arg)


def pre_signups_patch_callback(request, lookup):
    """
    don't allow PATCH on user_id, event_id or email"""
    data = payload()
    if ('user_id' in data) or ('event_id' in data) or ('email' in data):
        abort(403, description=(
            'You only can change extra_data'
        ))
    update_signups_schema(payload())


""" /events """


def check_events(data):
    if data.get('spots', -2) >= 0:
        if 'time_register_start' not in data or \
                'time_register_end' not in data:
            abort(422, description=(
                'You need to set time_register_start and time_register_end'
            ))
        elif data['time_register_end'] <= data['time_register_start']:
            abort(422, description=(
                'time_register_start needs to be before time_register_end'
            ))
    if data.get('time_start', dt.datetime.now()) > data.get('time_end',
                                                            dt.datetime.max):
        abort(422, description=(
            'time_end needs to be after time_start'
        ))
    if data.get('price', 0) < 0:
        abort(422, description=(
            'price needs to be positive or zero'
        ))
    validator = app.validator('', '')
    try:
        schema = json.loads(data.get('additional_fields'))
        validator.validate_schema(schema)
    except ValidationError as e:
            abort(422, description=(
                'validation exception: %s' % str(e)
            ))
    except Exception as e:
        # most likely a problem with the incoming payload, report back to
        # the client as if it was a validation issue
        abort(422, description=(
            'exception for additional_fields: %s' % str(e)
        ))


""" /permissions """


def check_permissions(data):
    if data.get('expiry_date') < dt.datetime.now():
        abort(422, description=debug_error_message(
            'expiry_date needs to be in the future'
        ))


""" /forwardaddresses """


def pre_forwardaddresses_delete_callback(item):
    """
    hook to send a confirmation email or apply the confirmed delete of an
    external email-address
    """
    if not confirm.confirm_actions(
        ressource='forwardaddresses',
        method='DELETE',
        doc=item,
        email_field='address',
    ):
        abort(202, description=('Please check your email and POST the token '
                                + 'to /confirms to process your request'))


""" /users """


def pre_users_get_callback(request, lookup):
    """ Prevent users from reading their password """
    projection = request.args.get('projection')
    if projection and 'password' in projection:
        abort(403, description='Bad projection field: password')


def pre_users_patch_callback(request, lookup):
    """
    Don't allow a user to change fields
    """
    if g.resource_admin_access:
        return

    disallowed_fields = ['username', 'firstname', 'lastname', 'birthday',
                         'legi', 'nethz', 'department', 'phone',
                         'ldapAddress', 'gender', 'membership']

    data = payload()

    for f in disallowed_fields:
        if f in data:
            app.logger.debug("Rejecting patch due to insufficent priviledges"
                             + "to change " + f)
            abort(403, description=(
                'You are not allowed to change your ' + f
            ))
