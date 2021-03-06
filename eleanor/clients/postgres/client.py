"""Handles eleanor's connection to postgres"""
import os
import getpass

import ConfigParser

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_db_engine():
    """Get the sqlalchemy db engine"""
    config = ConfigParser.RawConfigParser()
    if getpass.getuser() != 'eleanor':
        path_to_file = os.path.abspath(os.path.dirname(__file__))
        path_to_conf_file = '/'.join(path_to_file.split('/')[:-2])
        conf_file = '{0}/{1}'.format(
            path_to_conf_file, 'eleanor_local_auth.cfg'
        )
    else:
        conf_file = '/etc/opt/eleanor/eleanor_auth.cfg'
    config.read(conf_file)

    pg_user_name = config.get('Postgres', 'pg_uname')
    pg_password = config.get('Postgres', 'pg_pwd')
    pg_ip_address = config.get('Postgres', 'pg_ip_address')
    pg_db_name = config.get('Postgres', 'pg_db_name')

    engine = create_engine(
        'postgresql://{0}:{1}@{2}/{3}'.format(
            pg_user_name, pg_password, pg_ip_address, pg_db_name
        ),
        pool_size=25
    )
    return engine


class GetDBSession(object):
    """This class acts as a context manager for postgres connections"""

    def __init__(self):
        engine = get_db_engine()
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        # the above args should be == None if there are no exceptions so:
        if (
                (exc_type is not None) and
                (exc_value is not None) and
                (traceback is not None)
        ):
            self.session.rollback()
        self.session.close()
