from peewee import *
from os import getenv
BASE = 'local'


if BASE == 'local':
    db = PostgresqlDatabase(database=getenv('DATABASE', ''),
                            host=getenv('HOST', ''),
                            port=getenv('PORT', ''),
                            user=getenv('USER', ''),
                            password=getenv('PASSWORD', ''))
else:
    db = PostgresqlDatabase(database=ENVIRON.DB,
                       host=ENVIRON.HOST,
                       port=ENVIRON.PORT,
                       user=ENVIRON.USER,
                       password=ENVIRON.PASSWORD)

