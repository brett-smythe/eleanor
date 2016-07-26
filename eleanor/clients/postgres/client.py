import os.path

import ConfigParser

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


config = ConfigParser.RawConfigParser()
conf_file = '/etc/opt/eleanor_auth.cfg'
if os.path.isfile(conf_file):
    config.read(conf_file)
else:
    config.read(
        '/home/brett/dev/eleanor/eleanor/eleanor_local_auth.cfg'
    )

pg_user_name = config.get('Postgres', 'pg_uname')
pg_password = config.get('Postgres', 'pg_pwd')
pg_ip_address = config.get('Postgres', 'pg_ip_address')
pg_db_name = config.get('Postgres', 'pg_db_name')

engine = create_engine('postgresql://{0}:{1}@{2}/{3}'.format(
    pg_user_name, pg_password, pg_ip_address, pg_db_name
))


class GetDBSession(object):

    def __enter__(self):
        Session = sessionmaker(bind = engine)
        self.session = Session()
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        # the above args should be == None if there are no exceptions so:
        if ((exc_type != None) and (exc_value != None) and (traceback != None)):
            # TODO add logging here
            self.session.rollback()
        self.session.close()

