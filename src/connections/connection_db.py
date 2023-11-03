import asyncio

from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeMeta, declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.exc import DBAPIError
from sqlalchemy.sql.expression import literal
from typing import AsyncGenerator

# TODO: rm when prod
import sys
sys.path.append('../')
print(sys.path)

from data_storage.models import UseProject, UseConnect, UseSession
from storage_pgdb import get_async_session, async_session_maker

from datetime import datetime

ALL_CONNECTIONS = {}

#TODO: session destroyer


class AsyncPostgesConnection():
    # contains id of the session; isn't used in connection 
    SESSION_ID = ''

    PG_USER = ''
    PG_PASS = ''
    PG_HOST = ''
    PG_PORT = ''
    PG_NAME = ''
    DATABASE_URL = f'postgresql+asyncpg://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_NAME}'

    Base: DeclarativeMeta = declarative_base()

    def __init__(self, USER:str, PASS:str, HOST:str, PORT:str, NAME:str):
        self.PG_USER = USER
        self.PG_PASS = PASS
        self.PG_HOST = HOST
        self.PG_PORT = PORT
        self.PG_NAME = NAME
        
        self.recreate_db_url()
        self.create_engine_sessionmaker()

    def recreate_db_url(self):
        self.DATABASE_URL = f'postgresql+asyncpg://{self.PG_USER}:{self.PG_PASS}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_NAME}'
        return self.DATABASE_URL

    def create_engine_sessionmaker(self):
        self.engine = create_async_engine(self.DATABASE_URL)
        self.async_session_maker = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    async def get_async_session_generator(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.async_session_maker() as session:
            yield session

    async def get_async_session(self):
        return self.async_session_maker()
        
    
    async def check_connection(self):
        async with self.async_session_maker() as session:
            try:
                await session.connection()
            except asyncio.exceptions.TimeoutError:
                return False
        return True
    # TODO: THIS
    async def create_new_session_in_storage_db(self, prjct_name, session_name, user_name=''):
        async with async_session_maker() as session:
            subquery = select(UseConnect.prjct_id,
                              UseConnect.id,
                              literal(0),
                              literal(datetime.now()),
                              literal(datetime.now())).where(UseProject.prjct_name)


class HanaConnection():
    HANA_USER = ''
    HANA_PASS = ''
    HANA_HOST = ''
    HANA_PORT = ''
    HANA_SCHEMA = ''
    DATABASE_URL = f'hana+hdbcli://{HANA_USER}:{HANA_PASS}@{HANA_HOST}:{HANA_PORT}'

    Base: DeclarativeMeta = declarative_base()

    def __init__(self, USER:str, PASS:str, HOST:str, PORT:str, SCHEMA:str='', *args, **kwargs):
        self.HANA_USER = USER
        self.HANA_PASS = PASS
        self.HANA_HOST = HOST
        self.HANA_PORT = PORT
        self.HANA_SCHEMA = SCHEMA
        
        self.recreate_db_url()
        self.create_engine_sessionmaker()

    def recreate_db_url(self):
        self.DATABASE_URL = f'hana+hdbcli://{self.HANA_USER}:{self.HANA_PASS}@{self.HANA_HOST}:{self.HANA_PORT}'
        return self.DATABASE_URL

    def create_engine_sessionmaker(self):
        self.engine = create_engine(self.DATABASE_URL)
        self.session_maker = sessionmaker(autoflush=False, bind=self.engine)

    def get_session_generator(self) -> AsyncGenerator[AsyncSession, None]:
        with self.session_maker() as session:
            yield session

    def get_session(self):
        return self.session_maker()

    def __str__(self):
        return self.DATABASE_URL    
    
    def check_connection(self):
        with self.session_maker() as session:
            try:
                session.connection()
            except  DBAPIError as e:
                return False
        return True


CONNECTION_TYPES = {"HANA": HanaConnection, "PG_ASYNC": AsyncPostgesConnection}

def get_connection_session(prjct_name, cn_name):
    return ALL_CONNECTIONS[prjct_name, cn_name]

def set_connection_session(prjct_name, cn_name, cn_instance):
    ALL_CONNECTIONS[prjct_name, cn_name] = cn_instance

def delete_connection_session(prjct_name, cn_name):
    cn = ALL_CONNECTIONS.pop((prjct_name, cn_name))
    #TODO: do someth with it finaly 
    del cn

def is_connection_session(prjct_name, cn_name) -> bool:
    if (prjct_name, cn_name) in ALL_CONNECTIONS:
        return True
    return False

def get_all_connection_sessions()-> dict:
    r_keys = ALL_CONNECTIONS.keys()

    res = {}
    for key in r_keys:
        res ["".join([key_part + ", " for key_part in key])] = ALL_CONNECTIONS[key].__str__()
    return res
""" 
from sqlalchemy import select
import sys
sys.path.append('/home/sergh/projects/HANA/Hana_schema/src/')
from data_storage.models import UseProject, UseConnect

host1 = '10.100.100.11'
host2 = 'google.com'
pg1 = AsyncPostgesConnection(PG_HOST=host2, PG_PORT='5435',\
                             PG_NAME='storage_db', PG_PASS='root', PG_USER='root')






sql = select(UseProject)
sql2 = select(UseConnect)

async def main(tst, sql): 
    
    async with await tst.get_async_session() as session:
        #response = (await session.execute(sql)).all()
        #print([res[0].__dict__ for res in response])
        print('ok')

#main(pg1, sql)
asyncio.run(pg1.check_connection()) """

if __name__ == '__main__':
    #hc1 = HanaConnection(HANA_HOST='sap-s4h-s01.moscow.terralink', HANA_PORT='30015',\
    #                    HANA_USER='PROSKURIND',  HANA_PASS='Resident4')

    #print(hc1.check_connection())

    #host1 = '10.100.100.11'
    #host2 = 'google.com'
    #pg1 = AsyncPostgesConnection(PG_HOST=host1, PG_PORT='5435',\
    #                            PG_NAME='storage_db', PG_PASS='root', PG_USER='root')


    #a = asyncio.run( pg1.check_connection())
    #print(a)

    kw = {'HANA_HOST':'sap-s4h-s01.moscow.terralink', 'HANA_PORT':'30015',\
                        'HANA_USER':'PROSKURIND',  'HANA_PASS':'Resident4'}
    
    hc1 = HanaConnection(**kw)
    print(hc1.DATABASE_URL)