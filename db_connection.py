from peewee import *

BASE = 'local'


if BASE == 'local':
    db = PostgresqlDatabase(database='linkimoveis',
                       host='localhost',
                       port='5432',
                       user='postgres',
                       password='Pohgma@1980')
else:
    db = PostgresqlDatabase(database=ENVIRON.DB,
                       host=ENVIRON.HOST,
                       port=ENVIRON.PORT,
                       user=ENVIRON.USER,
                       password=ENVIRON.PASSWORD)

