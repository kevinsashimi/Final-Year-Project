import hashlib
import binascii
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:///knotty.db?check_same_thread=False')
Base = declarative_base()


class Table(Base):
    __tablename__ = 'account_manager'
    userid = Column(Integer)
    username = Column(String, default='default_value', primary_key=True)
    password = Column(String, default='default_value')
    status = Column(Boolean, default=False)

    def __repr__(self):
        return self.string_field


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    password_hash = hashlib.pbkdf2_hmac('sha512',
                                        password.encode('utf-8'),
                                        salt, 100000)
    password_hash = binascii.hexlify(password_hash)
    return (salt + password_hash).decode('ascii')


def verify_password(stored_password, provided_password):
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    password_hash = hashlib.pbkdf2_hmac('sha512',
                                        provided_password.encode('utf-8'),
                                        salt.encode('ascii'),
                                        100000)
    password_hash = binascii.hexlify(password_hash).decode('ascii')
    return password_hash == stored_password
