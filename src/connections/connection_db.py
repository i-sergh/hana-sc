import asyncio

from sqlalchemy import Column, VARCHAR, NVARCHAR, Integer
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

import pandas as pd

from datetime import datetime
import os
import errno


ALL_CONNECTIONS = {}

#TODO: session destroyer

#
# TODO TODO TODO      TODO TODO       TODO TODO            TODO TODO       
#      TODO       TODO         TODO   TODO      TODO   TODO         TODO  TODO 
#      TODO       TODO         TODO   TODO      TODO   TODO         TODO  TODO   
#      TODO       TODO         TODO   TODO      TODO   TODO         TODO         Default connections
#      TODO       TODO         TODO   TODO      TODO   TODO         TODO  TODO  
#      TODO       TODO         TODO   TODO      TODO   TODO         TODO  TODO 
#      TODO           TODO TODO       TODO TODO            TODO TODO       
#      



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
    
    # universal constants
    KEY_COL_FOR_TABLE_SEARCH_IN_TABLES = 'TABLE_NAME'
    KEY_COL_FOR_TABLE_SEARCH_IN_COLUMNS = 'TABLE_NAME'
    KEY_COL_FOR_COLUMN_SEARCH = 'COLUMN_NAME'
    HEADERS_FOR_TABLES_LIST = ['IDX','SCHEMA_NAME', 'TABLE_NAME','TABLE_TYPE',
                               'IS_TEMPORARY', 'IS_SYSTEM_TABLE', 'COMMENTS']
    HEADERS_FOR_COLUMNS_LIST = ['IDX','COLUMN_NAME', 'CS_DATA_TYPE_NAME', 'DATA_TYPE_NAME', 'LENGTH',
                                'DEFAULT_VALUE','MIN_VALUE','MAX_VALUE', 'IS_NULLABLE'] 
    #'DATA_TYPE_ID',  'TABLE_NAME', 'CS_DATA_TYPE_ID', 'SCHEMA_NAME', 
    

    HANA_USER = ''
    HANA_PASS = ''
    HANA_HOST = ''
    HANA_PORT = ''
    HANA_SCHEMA = ''
    DATABASE_URL = f'hana+hdbcli://{HANA_USER}:{HANA_PASS}@{HANA_HOST}:{HANA_PORT}'

    Base: DeclarativeMeta = declarative_base()

    class HanaTables(Base):
        __tablename__ = 'TABLES'
        __table_args__ = {'schema': 'SYS'}
        
        TABLE_NAME = Column(VARCHAR, primary_key=True)
        SCHEMA_NAME = Column(NVARCHAR)
        IS_TEMPORARY = Column(VARCHAR)
        TABLE_TYPE = Column(VARCHAR)
        COMMENTS = Column(NVARCHAR)
        IS_SYSTEM_TABLE = Column(VARCHAR)

    class HanaColumns(Base):
        __tablename__ = 'TABLE_COLUMNS'
        __table_args__ = {'schema': 'SYS'}

        CS_DATA_TYPE_NAME = Column(VARCHAR)
        LENGTH = Column(Integer)
        IS_NULLABLE = Column(VARCHAR)
        SCHEMA_NAME = Column(NVARCHAR, primary_key=True)
        COLUMN_NAME = Column(NVARCHAR, primary_key=True)
        TABLE_NAME = Column(NVARCHAR, primary_key=True)
        DEFAULT_VALUE = Column(NVARCHAR)
        MAX_VALUE = Column(VARCHAR)
        MIN_VALUE = Column(VARCHAR)
        DATA_TYPE_NAME = Column(VARCHAR)
        DATA_TYPE_ID = Column(Integer)
        CS_DATA_TYPE_NAME = Column(VARCHAR)
        CS_DATA_TYPE_ID = Column(Integer)

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
    
    async def check_connection(self):
        with self.session_maker() as session:
            try:
                session.connection()
            except  DBAPIError as e:
                return False
        return True
    
    def get_tables_from_db(self):

        with self.get_session() as session: 
            sql = select(self.HanaTables)
            result =session.execute(sql).all()
            #TODO: Might be err, when no results
            result_list = [result_data[0].__dict__ \
                           for result_data in result]
            
            for result in result_list:
                if '_sa_instance_state' in result:
                    result.pop('_sa_instance_state')
            return result_list
        #TODO: no connection exception

    def get_columns_from_db(self):
        with self.get_session() as session: 
            sql = select(self.HanaColumns)
            result =session.execute(sql).all()
            #TODO: Might be err, when no results
            result_list = [result_data[0].__dict__ \
                           for result_data in result]
            
            for result in result_list:
                if '_sa_instance_state' in result:
                    result.pop('_sa_instance_state')
            return result_list

CONNECTION_TYPES = {"HANA": HanaConnection, "PG_ASYNC": AsyncPostgesConnection}

def get_connection_session(prjct_name, cn_name):
    return ALL_CONNECTIONS[prjct_name, cn_name]

def set_connection_session(prjct_name, cn_name, cn_instance):
    ALL_CONNECTIONS[prjct_name, cn_name] = cn_instance

def delete_connection_session(prjct_name, cn_name):
    if (prjct_name, cn_name) in ALL_CONNECTIONS:
        cn = ALL_CONNECTIONS.pop((prjct_name, cn_name))
        #TODO: do someth with it finaly 
        del cn
        return True
    return False

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

def is_schema_saved(prjct_name, cn_name): 
    folder = prjct_name+"__"+cn_name
    file_tables = f"tables_{prjct_name}__{cn_name}.csv"
    file_columns = f"columns_{prjct_name}__{cn_name}.csv"
    path_tables = f"connections/connections_schemas/{folder}/{file_tables}"
    path_columns = f"connections/connections_schemas/{folder}/{file_columns}"
    print(os.path.isfile(path_tables), os.path.isfile(path_columns))

    return os.path.isfile(path_tables) and os.path.isfile(path_columns)



async def check_connection_session(prjct_name, cn_name):
    if (prjct_name, cn_name) in ALL_CONNECTIONS:
        result = await ALL_CONNECTIONS[(prjct_name, cn_name)].check_connection()
        return result
    return False

async def clone_names_of_tables(prjct_name, cn_name):
    # TODO: on any errors return false
    if not (prjct_name, cn_name) in ALL_CONNECTIONS:
        return False
    tables_list_dict = ALL_CONNECTIONS[(prjct_name, cn_name)].get_tables_from_db()
    folder = f'{prjct_name}__{cn_name}'
    file = f'tables_{prjct_name}__{cn_name}.csv'
    path = f'connections/connections_schemas/{folder}/{file}'
    # path creation
    try:
        os.makedirs(os.path.dirname(path))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise
    df = pd.DataFrame.from_dict(tables_list_dict)
    df['IDX'] = df.index
    df.to_csv(path, index=False)
    return True

async def clone_names_of_columns(prjct_name, cn_name):
    # TODO: on any errors return false
    if not (prjct_name, cn_name) in ALL_CONNECTIONS:
        return False
    tables_list_dict = ALL_CONNECTIONS[(prjct_name, cn_name)].get_columns_from_db()
    folder = f'{prjct_name}__{cn_name}'
    file = f'columns_{prjct_name}__{cn_name}.csv'
    path = f'connections/connections_schemas/{folder}/{file}'
    
    # path creation
    try:
        os.makedirs(os.path.dirname(path))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

    df = pd.DataFrame.from_dict(tables_list_dict)
    df['IDX'] = df.index
    df.to_csv(path, index=False)
    return True


def get_HEADERS_for_columns(prjct_name:str, cn_name:str):
    if not (prjct_name, cn_name) in ALL_CONNECTIONS:
        return False
    return ALL_CONNECTIONS[(prjct_name, cn_name)].HEADERS_FOR_COLUMNS_LIST

def get_KEY_COL_for_columns(prjct_name:str, cn_name:str):
    if not (prjct_name, cn_name) in ALL_CONNECTIONS:
        return False
    return ALL_CONNECTIONS[(prjct_name, cn_name)].KEY_COL_FOR_COLUMN_SEARCH

def get_KEY_COL_for_tables(prjct_name:str, cn_name:str):
    if not (prjct_name, cn_name) in ALL_CONNECTIONS:
        return False
    return ALL_CONNECTIONS[(prjct_name, cn_name)].KEY_COL_FOR_TABLE_SEARCH_IN_TABLES

def get_KEY_COL_TABLE_for_columns(prjct_name:str, cn_name:str):
    if not (prjct_name, cn_name) in ALL_CONNECTIONS:
        return False
    return ALL_CONNECTIONS[(prjct_name, cn_name)].KEY_COL_FOR_TABLE_SEARCH_IN_COLUMNS


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