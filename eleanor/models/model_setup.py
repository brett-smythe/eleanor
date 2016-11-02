from eleanor.models import models, twitter_models
from eleanor.models.base import Base
from eleanor.clients.postgres import client

from eleanor.utils import get_logger

with client.GetDBSession as db_session:

    logger = get_logger(__name__)
    logger.info('Setting up database for eleanor')

    Base.metadata.create_all()
