from peewee import *
from os import getenv
BASE = 'nuvem'


if BASE == 'nuvem':
    db = PostgresqlDatabase(database=getenv('DATABASE', 'defaultdb'),
                            host=getenv('HOST', 'linkimovel-brain-ag.l.aivencloud.com'),
                            port=getenv('PORT', '21242'),
                            user=getenv('USER', 'avnadmin'),
                            password=getenv('PASSWORD', 'AVNS_FLSIPqCapJPjpvmSHTG'))
else:
    db = PostgresqlDatabase(database=getenv('DATABASE', 'linkimoveis'),
                            host=getenv('HOST', 'localhost'),
                            port=getenv('PORT', '5432'),
                            user=getenv('USER', 'postgres'),
                            password=getenv('PASSWORD', 'Pohgma@1980'))

