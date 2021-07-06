#TODO db connector
import sshtunnel
from sqlalchemy import create_engine
import pandas as pd

PATH_TO_PK= '/home/m/.ssh/bet_postgres'
PK_PW = 'E6XPDk1PxRPdyXbDnaQL'
FRONTEND_IP = '78.128.250.175'
DB_IP = '172.16.1.180'
USERNAME = 'uhrinmat'

server = sshtunnel.SSHTunnelForwarder(
    (FRONTEND_IP, 22),
    ssh_username=USERNAME,
    ssh_pkey=PATH_TO_PK,
    ssh_private_key_password=PK_PW,
    remote_bind_address=(DB_IP, 5432),
)

server.start()

BIND_PORT = server.local_bind_port

DB = 'bet'
DB_USER = 'uhrinmat'
DB_PW = 'uhrinmat'
SCHEMA = 'isdb'
db = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PW}@127.0.0.1:{BIND_PORT}/{DB}')
data = pd.read_sql_table('Matches',db,schema=SCHEMA)

server.stop()
