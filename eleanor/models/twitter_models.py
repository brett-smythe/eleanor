"""Models for twitter text sources"""
from sqlalchemy import (
    Column, Integer, String, ForeignKey, BigInteger, Boolean
)

from sqlalchemy.orm import relationship

from base import Base


class TwitterSource(Base):
    """Base model for twitter text sources"""
    __tablename__ = 'twitter_source'

    id = Column(Integer, primary_key=True)
    text_source_id = Column(
        Integer, ForeignKey('text_source.id'), nullable=False
    )
    retweet_source_id = Column(
        Integer, ForeignKey('twitter_source.id'), nullable=True
    )
    tweeter_user_name = Column(String)
    tweet_id = Column(BigInteger, unique=True)
    is_retweet = Column(Boolean)

    text_source = relationship('TextSource', back_populates='twitter_source')
    hashtags = relationship(
        'TweetHashtags',
        back_populates='twitter_source',
        cascade='all, delete, delete-orphan'
    )
    urls = relationship(
        'TweetURLs',
        back_populates='twitter_source',
        cascade='all, delete, delete-orphan'

    )
    mentions = relationship(
        'TweetUserMentions',
        back_populates='twitter_source',
        cascade='all, delete, delete-orphan'

    )


class TweetHashtags(Base):
    """Model for hashtags within a tweet"""
    __tablename__ = 'tweet_hashtags'

    id = Column(Integer, primary_key=True)
    twitter_source_id = Column(
        Integer, ForeignKey('twitter_source.id'), nullable=False
    )
    hashtag = Column(String)

    twitter_source = relationship('TwitterSource', back_populates='hashtags')


class TweetURLs(Base):
    """Model for urls within a tweet"""
    __tablename__ = 'tweet_urls'

    id = Column(Integer, primary_key=True)
    twitter_source_id = Column(
        Integer, ForeignKey('twitter_source.id'), nullable=False
    )
    url = Column(String)

    twitter_source = relationship('TwitterSource', back_populates='urls')


class TweetUserMentions(Base):
    """Model for users mentioned within a tweet"""
    __tablename__ = 'tweet_user_mentions'

    id = Column(Integer, primary_key=True)
    twitter_source_id = Column(
        Integer, ForeignKey('twitter_source.id'), nullable=False
    )
    user_name = Column(String)

    twitter_source = relationship('TwitterSource', back_populates='mentions')


class PolledTimelineUsers(Base):
    """Model containing twitter users that are being polled by aquatic services
    """
    __tablename__ = 'polled_timeline_users'

    id = Column(Integer, primary_key=True)
    user_name = Column(String)
