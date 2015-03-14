"""
Starting point for the API
"""


from eve import Eve
from eve_sqlalchemy import SQL  # , ValidatorSQL
from eve_docs import eve_docs
from flask.ext.bootstrap import Bootstrap
from flask import g

from amivapi import (
    models,
    confirm,
    schemas,
    authentification,
    authorization,
    media,
    forwards,
    localization,
    validation,
    documentation
)

from amivapi.utils import get_config


def create_app(environment, disable_auth=False):
    """
    Create a new eve app object and initialize everything.

    :param environment: The environment this app should use, this is basically
                        the basename of the config file to use
    :param disable_auth: This can be used to allow every request without
                         authentification for testing purposes
    :returns: eve.Eve object, the app object
    """
    config = get_config(environment)
    config['DOMAIN'] = schemas.get_domain()
    config['BLUEPRINT_DOCUMENTATION'] = documentation.get_blueprint_doc()

    if disable_auth:
        app = Eve(settings=config,
                  data=SQL,
                  validator=validation.ValidatorAMIV,
                  media=media.FileSystemStorage)
    else:
        app = Eve(settings=config,
                  data=SQL,
                  validator=validation.ValidatorAMIV,
                  auth=authentification.TokenAuth,
                  media=media.FileSystemStorage)

    # Bind SQLAlchemy
    db = app.data.driver
    models.Base.metadata.bind = db.engine
    db.Model = models.Base

    Bootstrap(app)
    with app.app_context():
        g.db = db.session

    # Generate and expose docs via eve-docs extension
    app.register_blueprint(eve_docs, url_prefix="/docs")
    app.register_blueprint(confirm.confirmprint)
    app.register_blueprint(authentification.authentification)
    app.register_blueprint(authorization.permission_info)
    app.register_blueprint(media.download)

    #
    #
    # Event hooks
    #
    # security note: hooks which are run before auth hooks should never change
    # the database
    #

    app.on_insert += validation.pre_insert_check
    app.on_update += validation.pre_update_check
    app.on_replace += validation.pre_replace_check

    # eventsignups
    # for signups we need extra hooks to validate the field extra_data
    app.on_pre_POST_eventsignups += validation.pre_signups_post
    app.on_pre_PATCH_eventsignups += validation.pre_signups_patch
    app.on_pre_UPDATE_eventsignups += validation.pre_signups_update
    app.on_pre_PUT_eventsignups += validation.pre_signups_put

    # Hooks for anonymous users
    app.on_insert_eventsignups += confirm.signups_confirm_anonymous
    app.on_insert_forwardaddresses += confirm.\
        forwardaddresses_insert_anonymous

    app.on_update += confirm.pre_update_confirmation
    app.on_delete_item += confirm.pre_delete_confirmation
    app.on_replace += confirm.pre_replace_confirmation

    app.on_updated += confirm.post_updated_confirmation
    app.on_inserted += confirm.post_inserted_confirmation
    app.on_deleted_item += confirm.post_deleted_confirmation
    app.on_fetched += confirm.post_fetched_confirmation
    app.on_replaced += confirm.post_replaced_confirmation

    # users
    app.on_pre_GET_users += authorization.pre_users_get
    app.on_pre_PATCH_users += authorization.pre_users_patch

    # authentification
    app.on_insert_users += authentification.hash_password_before_insert
    app.on_replace_users += authentification.hash_password_before_replace
    app.on_update_users += authentification.hash_password_before_update

    app.on_insert += authentification.set_author_on_insert
    app.on_replace += authentification.set_author_on_replace

    if not disable_auth:
        app.on_pre_GET += authorization.pre_get_permission_filter
        app.on_pre_POST += authorization.pre_post_permission_filter
        app.on_pre_PUT += authorization.pre_put_permission_filter
        app.on_pre_DELETE += authorization.pre_delete_permission_filter
        app.on_pre_PATCH += authorization.pre_patch_permission_filter
        app.on_update += authorization.update_permission_filter

    # email-management
    app.on_deleted_item_forwards += forwards.on_forward_deleted
    app.on_inserted_forwardusers += forwards.on_forwarduser_inserted
    app.on_replaced_forwardusers += forwards.on_forwarduser_replaced
    app.on_updated_forwardusers += forwards.on_forwarduser_updated
    app.on_deleted_item_forwardusers += forwards.on_forwarduser_deleted
    app.on_inserted__forwardaddresses += forwards.on_forwardaddress_inserted
    app.on_replaced__forwardaddresses += forwards.on_forwardaddress_replaced
    app.on_updated__forwardaddresses += forwards.on_forwardaddress_updated
    app.on_deleted_item__forwardaddresses += forwards.on_forwardaddress_deleted

    # Hooks for translatable fields, done by resource because there are only 2
    app.on_fetched_item_joboffers += localization.insert_localized_fields
    app.on_fetched_item_events += localization.insert_localized_fields
    app.on_insert_joboffers += localization.create_localization_ids
    app.on_insert_events += localization.create_localization_ids
    app.on_insert_translations += localization.unique_language_per_locale_id

    return app
