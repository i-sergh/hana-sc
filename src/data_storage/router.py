from fastapi import APIRouter, Depends

from sqlalchemy import insert, select, delete, update

from data_storage.models import UseProject, UseConnect
from storage_pgdb import get_async_session
from datetime import datetime


router = APIRouter(
    prefix='/data',
    tags=['Project settings']
)

@router.post('/create-project')
async def create_project(prjct_name:str, prjct_desc:str=None, session=Depends(get_async_session)):
    sql = insert(UseProject).\
        values( prjct_name=prjct_name, prjct_description=prjct_desc, created_at=datetime.now())
    await session.execute(sql)
    await session.commit()
    return {'result':'success'}

@router.get('/get-project-info')
async def get_project_info_by_name(name:str, session=Depends(get_async_session)):
    sql = select(UseProject.prjct_name, UseProject.prjct_description, UseProject.created_at).\
            where(UseProject.prjct_name==name)
    result = await session.execute(sql)
    result_list = list(result.all()[0])
    
    return {'result':result_list}


@router.get('/get-all-projects')
async def get_all_progects_info( session=Depends(get_async_session)):
    sql = select(UseProject.prjct_name, UseProject.prjct_description, UseProject.created_at)
    result = await session.execute(sql)
    result_list = {}
    for idx, row in enumerate(result.all()): 
        res_name = 'prjct' + str(idx)
        result_list[res_name] = list(row)
    
    return {'result':result_list}

@router.delete('/delete-project')
async def delete_project_by_name(name:str, session=Depends(get_async_session)):
    sql = delete(UseProject).where(UseProject.prjct_name==name)
    await session.execute(sql)
    await session.commit()
    return {'result':'success'}

@router.patch('/update-project-description')
async def update_project_description(name:str, desc:str='', session=Depends(get_async_session)):
    sql = update(UseProject).where(UseProject.prjct_name==name).values(prjct_description=desc)
    await session.execute(sql)
    await session.commit()
    return {'result':'success'}

@router.post('/create-connection')
async def create_connection(prjct_name:str, name:str, requirements:str, 
                      host:str="", port:str="", db_name:str="",
                      db_schema:str="", user:str="", pwd:str="",
                      api_key:str="", session=Depends(get_async_session)):
    sql = select(UseProject.prjct_name).join()
    result = await session.execute(sql)
    print(result.all())

    """ select * from connections left join projects on connections.prjct_id = projects.id where prjct_name='name1';
 """

    """ sql = insert(UseConnect).\
        values( prjct_name=prjct_name, prjct_description=prjct_desc, created_at=datetime.now()) """
    
    return{'response': '0k'}