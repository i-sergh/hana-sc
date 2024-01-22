from fastapi import APIRouter, Request

from connections.search_drv import find_table_columns_by_part_name, headers_from_df,\
                                    content_from_df

from data_storage.scripts import query_connection_info_by_prjct_name_cn_name

from connections.connection import set_connection_session,\
    get_connection_session, get_all_connection_sessions,\
    is_connection_session, CONNECTION_TYPES,\
    is_schema_saved, delete_connection_session,\
    check_connection_session, clone_names_of_tables,\
    clone_names_of_columns, get_KEY_COL_for_tables,\
    get_HEADERS_for_columns, get_KEY_COL_TABLE_for_columns

import sys

router = APIRouter(
    prefix='/session',
    tags=['Connection']
)




##{"HANA_HOST":"sap-s4h-s01.moscow.terralink", "HANA_PORT":"30015","HANA_USER":"PROSKURIND","HANA_PASS":"Resident4"}
@router.post('/new-und-check')
async def check_und_create_connection_session(request:Request, \
                                              prjct_name:str, \
                                              cn_name:str):
    if is_connection_session(prjct_name, cn_name):
        cn = get_connection_session(cn_name=cn_name, prjct_name=prjct_name)
        res = await check_connection_session(prjct_name=prjct_name, cn_name=cn_name)

        return {"message": "found",
                "result": res}
    res = ""
    data = await query_connection_info_by_prjct_name_cn_name(prjct_name=prjct_name, cn_name=cn_name)
    cn_type = data['DRIVER']
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
    result = await clone_names_of_columns(prjct_name=prjct_name, cn_name=cn_name)
    return {"result": result}

@router.post("/find-table")
async def find_table_in_schema(prjct_name:str, cn_name:str, word:str):
    word = word.upper().strip()

    # also checks session availability 
    key_col = get_KEY_COL_for_tables(prjct_name=prjct_name, cn_name=cn_name)
    print( await headers_from_df(prjct_name=prjct_name, cn_name=cn_name))
    if not key_col:
        print('NO SESSION CONNECTION', file=sys.stderr)
        return {
            "message": "no connection",
            "result": ""
            }
    result = await find_table_columns_by_part_name(prjct_name=prjct_name, cn_name=cn_name, key_col=key_col, word=word)
    return {
            "message": "success",
            "result": result
            }

@router.post("/get-table-structure")
async def get_table_structure(prjct_name:str, cn_name:str, table_name:str):
    
    headers = get_HEADERS_for_columns(prjct_name=prjct_name, cn_name=cn_name)
    key_col = get_KEY_COL_TABLE_for_columns(prjct_name=prjct_name, cn_name=cn_name)
    content = await content_from_df(prjct_name=prjct_name, cn_name=cn_name,
                                    headers=headers, key_col=key_col, 
                                    key_word=table_name, prefix='columns')
    
    result = {
        'headers':headers,
        'content':content
    }

    return {
        'message': 'success',
        'result':result
    }




# UTILS 






