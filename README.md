# Eleanor

Web service layer over a database for storing and retrieving text from various sources. Currently twitter is the only data source with implemented models however it can be easily extended to others.

## Install
Recommended to install and run in a virtualenv

```
python setup.py install
cd eleanor/models/
python model_setup.py
```

### External Dependencies
eleanor depends on:
* If this is to be deployed in a more production environment you'll likely want to set this up with a WSGI server and likely a static server
* A running postgresql instance
  * A user with remote access to the database
  * A cfg file located at either `eleanor/eleanor_local_auth.cfg` or `/etc/opt/eleanor/eleanor_auth.cfg` with the following fields:
```
[Postgres]
pg_uname = <postgresql_user_name>
pg_pwd = <password>
pg_ip_address = <postgresql_ip_address>
pg_db_name = <postgresql_database_name>
```

## Usage
For development
```
eleanor
```

For production, as noted above you'll likely want to use a WSGI and static server
