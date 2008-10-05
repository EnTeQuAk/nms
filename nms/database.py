# -*- coding: utf-8 -*-
"""
    lodgeit.database
    ~~~~~~~~~~~~~~~~

    Database fun :)

    :copyright: 2007 by Armin Ronacher, Christopher Grebs.
    :license: BSD
"""
from os import path
import time
import difflib
from types import ModuleType
import sqlalchemy
from sqlalchemy import orm, MetaData, create_engine
from sqlalchemy.orm import scoped_session, create_session
from cgi import escape
from datetime import datetime
from nms import _local_manager, ctx

engine = create_engine('sqlite:///%s' % path.join(
    ctx.context['home_path'], 'database.db'
), convert_unicode=True, echo=ctx.settings['debug'])

if ctx.settings['debug']:
    import logging
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    handler = logging.FileHandler(path.join(
        ctx.context['home_path'], 'logs', 'db.log'
    ))
    logging.getLogger('sqlalchemy.engine').addHandler(handler)

metadata = MetaData(bind=engine)

session = scoped_session(lambda: create_session(engine,
    autoflush=True, transactional=True))


#: create a fake module for easy access to database session methods
db = ModuleType('db')
key = value = mod = None
for mod in sqlalchemy, orm:
    for key, value in mod.__dict__.iteritems():
        if key in mod.__all__:
            setattr(db, key, value)
del key, mod, value

db.__doc__ = __doc__
for name in 'delete', 'save', 'flush', 'execute', 'begin', 'query', \
            'commit', 'rollback', 'clear', 'refresh', 'expire':
    setattr(db, name, getattr(session, name))
db.session = session


recipients_table = db.Table('recipients', metadata,
    db.Column('id', db.Integer, primary_key=True),
    db.Column('name', db.String(100), nullable=False),
    db.Column('mail', db.String(100), nullable=False),
    db.Column('active', db.Boolean, nullable=False),
    db.Column('comment', db.String(100), nullable=True),
)


class Recipient(object):
    def __init__(self, name=None, mail=None, active=False, comment=None):
        self.name = name or u'unknown'
        self.mail = mail or u'unknown'
        self.active = active
        self.comment = comment

    def __eq__(self, other):
        for item in ('name', 'mail', 'active', 'comment'):
            if not getattr(self, item) == getattr(other, item):
                return False
        return True

db.mapper(Recipient, recipients_table)
