from peewee import *

BASE = 'local'


if BASE == 'local':
    db = PostgresqlDatabase(database='defaultdb',
                       host='linkimovel-brain-ag.l.aivencloud.com',
                       port='21242',
                       user='avnadmin',
                       password='AVNS_FLSIPqCapJPjpvmSHTG')
else:
    db = PostgresqlDatabase(database=ENVIRON.DB,
                       host=ENVIRON.HOST,
                       port=ENVIRON.PORT,
                       user=ENVIRON.USER,
                       password=ENVIRON.PASSWORD)

