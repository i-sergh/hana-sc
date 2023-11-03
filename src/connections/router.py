from fastapi import APIRouter, Request

from sqlalchemy import insert, select, delete, update

from data_storage.models import UseProject
from storage_pgdb import get_async_session, async_session_maker

from datetime import datetime

from data_storage.models import UseConnect

from connections.connection_db import set_connection_session, get_connection_session, get_all_connection_sessions, is_connection_session, CONNECTION_TYPES

import json

router = APIRouter(
    prefix='/session',
    tags=['Project', 'Connection']
)


##{"HANA_HOST":"sap-s4h-s01.moscow.terralink", "HANA_PORT":"30015","HANA_USER":"PROSKURIND","HANA_PASS":"Resident4"}
@router.post('/new-und-check')
async def check_und_create_connection_session(r:Request, prjct_name:str, cn_name:str, cn_type:str) -> dict:
    if is_connection_session(prjct_name, cn_name):
        cn = get_connection_session(cn_name=cn_name, prjct_name=prjct_name)
        res = cn.check_connection()
        return {"message": "found",
                "result": res}
    res = ""

    data = json.loads(await r.body())
    cn = CONNECTION_TYPES[cn_type](**data)
    set_connection_session(cn_name=cn_name, prjct_name=prjct_name, cn_instance=cn)
    res = cn.check_connection()
    return {"message": "created",
            "result": res}

@router.post('/check')
async def check_connection(prjct_name:str, cn_name:str):

    cn = get_connection_session(cn_name=cn_name, prjct_name=prjct_name)
    res = cn.check_connection()
    return {"result": res}

@router.post('/all')
async def get_all_connection_sessions_req():
    res = get_all_connection_sessions()
    return {"result": res}

@router.delete('/delete')
def delete_connection(prjct_name:str, cn_name:str):
    return {"result": get_connection_session(cn_name=cn_name, prjct_name=prjct_name)}