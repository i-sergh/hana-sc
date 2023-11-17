from fastapi import APIRouter, Request

from connections.search_drv import get_columns

from connections.connection_db import set_connection_session,\
    get_connection_session, get_all_connection_sessions,\
    is_connection_session, CONNECTION_TYPES,\
    is_schema_saved, delete_connection_session,\
    check_connection_session, clone_names_of_tables

router = APIRouter(
    prefix='/session',
    tags=['Connection']
)

class Cls:
    val = 0

def work(cn):

    return True

##{"HANA_HOST":"sap-s4h-s01.moscow.terralink", "HANA_PORT":"30015","HANA_USER":"PROSKURIND","HANA_PASS":"Resident4"}
@router.post('/new-und-check')
async def check_und_create_connection_session(request:Request, \
                                              prjct_name:str, \
                                              cn_name:str,\
                                              cn_type:str):
    if is_connection_session(prjct_name, cn_name):
        cn = get_connection_session(cn_name=cn_name, prjct_name=prjct_name)
        res = await check_connection_session(prjct_name=prjct_name, cn_name=cn_name)

        return {"message": "found",
                "result": res}
    res = ""

    data = await query_connection_info_by_prjct_name_cn_name(prjct_name=prjct_name, cn_name=cn_name)
    cn = CONNECTION_TYPES[cn_type](**data) #TODO: make func; заменить на get_driver
    set_connection_session(cn_name=cn_name, prjct_name=prjct_name, cn_instance=cn)
    
    res = await check_connection_session(prjct_name=prjct_name, cn_name=cn_name)
    return {"message": "created",
            "result": res}

@router.post('/check')
async def check_connection(prjct_name:str, cn_name:str):

    cn = get_connection_session(cn_name=cn_name, prjct_name=prjct_name)
    res = await ( cn.check_connection())
    return {"result": res}

@router.post('/all')
async def get_all_connection_sessions_req():
    res = get_all_connection_sessions()

    return {"result": res}

@router.delete('/delete')
def delete_connection(prjct_name:str, cn_name:str):
    if delete_connection_session(prjct_name=prjct_name, cn_name=cn_name):
        return {"message": "success"}
    else:
        return {"message": "no such connection"}
    
@router.get('/check-schema')
async def check_schema_availability(prjct_name:str, cn_name:str):
    is_schema = is_schema_saved(prjct_name=prjct_name, cn_name=cn_name)
    return is_schema

@router.post('/check-tables')
async def check_tables_availability(prjct_name:str, cn_name:str):
    result = await clone_names_of_tables(prjct_name=prjct_name, cn_name=cn_name)
    return {"result": result}

@router.post("/find-table")
async def find_table_from_schema(prjct_name:str, cn_name:str, word:str):
    word = word.upper().strip()
    result = get_columns(prjct_name=prjct_name, cn_name=cn_name, word=word)
    return {
            "message": "success",
            "result": result
            }
# UTILS 

from sqlalchemy import  select
from data_storage.models import UseProject, UseConnect
from storage_pgdb import  async_session_maker


async def query_connection_info_by_prjct_name_cn_name( prjct_name:str, cn_name:str):
    subquery = select(UseProject.id).where(UseProject.prjct_name==prjct_name).scalar_subquery()
    sql = select(UseConnect)\
          .where((UseConnect.prjct_id ==subquery)
                  & (UseConnect.cn_name == cn_name)) 
    
    async with async_session_maker() as session:
        result_sql = (await session.execute(sql)).all()
        try:
            result_sql = result_sql[0][0].__dict__
        except:
            return {}
    """{
    'cn_port': 30015,
    'cn_pwd': 'Resident4',
    'cn_schema': '', 
    'cn_host': 'sap-s4h-s01.moscow.terralink', 
    'cn_user': 'PROSKURIND',
    'cn_db': '',
    'cn_apikey': ''}
    """
    result = {}
    result['USER'] = result_sql['cn_user']
    result['PASS'] = result_sql['cn_pwd']
    result['HOST'] = result_sql['cn_host']
    result['PORT'] = result_sql['cn_port']
    result['NAME'] = result_sql['cn_db']
    result['SCHEMA'] = result_sql['cn_schema']
    result['APIKEY'] = result_sql['cn_apikey']
    return result
