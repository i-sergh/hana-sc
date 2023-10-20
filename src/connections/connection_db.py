import asyncio

from sqlalchemy import inspect, create_engine
from sqlalchemy.orm import DeclarativeMeta, declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.exc import DBAPIError
from typing import AsyncGenerator

class AsyncPostgesConnection():
    PG_USER = ''
    PG_PASS = ''
    PG_HOST = ''
    PG_PORT = ''
    PG_NAME = ''
    DATABASE_URL = f'postgresql+asyncpg://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_NAME}'

    Base: DeclarativeMeta = declarative_base()

    def __init__(self, PG_USER:str, PG_PASS:str, PG_HOST:str, PG_PORT:str, PG_NAME:str):
        self.PG_USER = PG_USER
        self.PG_PASS = PG_PASS
        self.PG_HOST = PG_HOST
        self.PG_PORT = PG_PORT
        self.PG_NAME = PG_NAME
        
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


class HanaConnection():
    HANA_USER = ''
    HANA_PASS = ''
    HANA_HOST = ''
    HANA_PORT = ''
    HANA_SCHEMA = ''
    DATABASE_URL = f'hana+hdbcli://{HANA_USER}:{HANA_PASS}@{HANA_HOST}:{HANA_PORT}'

    Base: DeclarativeMeta = declarative_base()

    def __init__(self, HANA_USER:str, HANA_PASS:str, HANA_HOST:str, HANA_PORT:str, HANA_SCHEMA:str=''):
        self.HANA_USER = HANA_USER
        self.HANA_PASS = HANA_PASS
        self.HANA_HOST = HANA_HOST
        self.HANA_PORT = HANA_PORT
        self.HANA_SCHEMA = HANA_SCHEMA
        
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
        
    
    def check_connection(self):
        with self.session_maker() as session:
            try:
                session.connection()
            except  DBAPIError as e:
                return False
        return True

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
    hc1 = HanaConnection(HANA_HOST='sap-s4h-s01.moscow.terralink', HANA_PORT='30015',\
                        HANA_USER='PROSKURIND',  HANA_PASS='Resident4')

    print(hc1.check_connection())

    host1 = '10.100.100.11'
    host2 = 'google.com'
    pg1 = AsyncPostgesConnection(PG_HOST=host2, PG_PORT='5435',\
                                PG_NAME='storage_db', PG_PASS='root', PG_USER='root')


    a = asyncio.run( pg1.check_connection())
    print(a)