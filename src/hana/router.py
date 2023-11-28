from fastapi import APIRouter, Depends, Response
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError

from hana.models import HanaMARA

from hana.schema2json.schema2json import get_test_json, test_get_empty_json, _fill_by_schema
from hanadb import get_session
from hana.schema2json.prettyStatus.prettyStatusHTTP import StatusCode

from hana.schema2json.jsonBase import JSONData, JSONStruct

router = APIRouter(
    prefix='/hana', 
    tags=['HANA']
    )


SCHEMA_CACHE = {}

@router.get('/mara-ten')
def get_mara_ten( session=Depends(get_session)):
    try:
        sql = select(HanaMARA.__table__).limit(10)
        result =session.execute(sql)
        result_list = result.all()
        print(result_list)
    except DBAPIError:
        return StatusCode(503).__dict__()
    
    return StatusCode(200).__dict__()

@router.get('/mara-struct')
def get_mara_struct(session=Depends(get_session)):
    try:
        sql = text("SELECT COLUMN_NAME, DATA_TYPE_NAME FROM SYS.TABLE_COLUMNS WHERE TABLE_NAME = '' ORDER BY POSITION; ")
        #sql = text("SELECT COLUMN_NAME FROM SYS.TABLE_COLUMNS WHERE TABLE_NAME = 'MARA' ORDER BY POSITION; ")
        
        ### !!!! все схемы базы
        #sql = text("SELECT DISTINCT SCHEMA_NAME FROM SYS.TABLE_COLUMNS")

        #sql = text("SELECT DISTINCT TABLE_NAME FROM SYS.TABLE_COLUMNS WHERE SCHEMA_NAME='SYS'")
        #sql = text("SELECT * FROM TABLES  LIMIT 1")


        #sql = text("SELECT DISTINCT DATA_TYPE_NAME FROM SYS.TABLE_COLUMNS; ") # получение всех типов данных в базе

        '''
        [('VARCHAR',), ('TIME',), ('BLOB',), ('BOOLEAN',), ('BIGINT',), ('NVARCHAR',), ('NCLOB',), ('CHAR',), 
        ('SECONDDATE',), ('VARBINARY',), ('REAL',), ('BINARY',), ('SMALLDECIMAL',), ('TINYINT',), ('TIMESTAMP',),
        ('DOUBLE',), ('DECIMAL',), ('DATE',), ('NCHAR',), ('SMALLINT',), ('CLOB',), ('ST_POINT',), ('INTEGER',), 
        ('TEXT',)]
        '''

        #DATA_TYPE_NAME = 'TIMESTAMP' AND
        sql = text("SELECT DISTINCT COLUMN_NAME, TABLE_NAME FROM SYS.TABLE_COLUMNS WHERE  DATA_TYPE_NAME='INTEGER' AND (TABLE_NAME='MARA' OR TABLE_NAME='EKPO' ); ")

        #sql = text("SELECT * FROM COVDETVAR;")
        result =session.execute(sql)

        result_list = result.all() 
        print(result_list)

    except DBAPIError:
        return StatusCode(503).__dict__()
    return StatusCode(200).__dict__()


@router.get('/hana-dtypes')
def get_all_dtypes(session=Depends(get_session)):
    try:
        sql = sql = text("SELECT DISTINCT DATA_TYPE_NAME FROM SYS.TABLE_COLUMNS; ")
        result =session.execute(sql)

        result_list = result.all() 
        print(result_list)
    except DBAPIError:
        return StatusCode(503).__dict__()
    return StatusCode(200).__dict__()



@router.post('/table-struct' )
def get_table_structure(table_name:str,session=Depends(get_session)):
    table_name = table_name.upper()
    if table_name == "":
        return { 
                 'code': StatusCode(400).code(),
                 'status':StatusCode(400).status(),
                 'table_name': None,
                 'cols': None
            }
    try:

        sql = text(f"SELECT COLUMN_NAME, DATA_TYPE_NAME, LENGTH FROM SYS.TABLE_COLUMNS WHERE TABLE_NAME='{table_name}'")
        result =session.execute(sql)

        result_list = result.all() 
        print(result_list)

        #print('MARA in ABAPS417', ('MARA',) in result_list) 
        #print('elements in ABAPS417', len(result_list)) 
    except DBAPIError:
        
        return StatusCode(503).__dict__()
    
    table = JSONStruct()
    table.set_table_name(table_name)

    result_col_name = [ elmnt[0]  for elmnt in result_list]
    result_col_dtype = [ elmnt[1]  for elmnt in result_list]
    #result_col_pkey = [ elmnt[2]  for elmnt in result_list]

    table.add_cols(result_col_name, result_col_dtype, ())

    #print(table.get_data())
    
    SCHEMA_CACHE[table_name] = table
    return table.get_data()



@router.get('/test/test-json')
def get_test_json():
    return get_test_json()

@router.get('/test/test-empty-json')
def get_empty_json():
    return test_get_empty_json()

@router.get('/test/test')
def get_test_schema():
    return _fill_by_schema()

