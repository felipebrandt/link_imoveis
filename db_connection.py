from peewee import *
from os import getenv
BASE = 'nuvem'


if BASE == 'nuvem':
    db = PostgresqlDatabase(database=getenv('DATABASE', ''),
                            host=getenv('HOST', ''),
                            port=getenv('PORT', ''),
                            user=getenv('USER', ''),
                            password=getenv('PASSWORD', ''))
else:
    db = PostgresqlDatabase(database=getenv('DATABASE', ''),
                            host=getenv('HOST', ''),
                            port=getenv('PORT', ''),
                            user=getenv('USER', ''),
                            password=getenv('PASSWORD', ''))

