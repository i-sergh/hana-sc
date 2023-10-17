from fastapi import APIRouter, Depends

from sqlalchemy import insert, select, delete, update
from sqlalchemy.sql.expression import literal

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

@router.get('/get-project-and-connections')
async def get_project_and_connections(prjct_name:str, session=Depends(get_async_session)):
    """
        Return statuses:
            - no project  : db hasn't found project with name <prjct_name>;
            - found empty : db has project with name <prjct_name>, but there is no connections in it;
            - found       : db contains project with name <prjct_name> and this project has nonempty list of connections.
    """
    sql = select(UseProject.prjct_name, UseProject.prjct_description, UseConnect)\
          .join(UseConnect, UseProject.id==UseConnect.prjct_id, full=True)\
          .where(UseProject.prjct_name == prjct_name)
    result = (await session.execute(sql)).all()
    
    if not result:
        return {
            'project status': 'no project',
            'projcet name': '',
            'project description': '',
            'project connections': []}
    
    prjct_name = result[0][0]
    prjct_description = result[0][1]
    if not result[0][2]:
        return {
            'project status': 'found empty',
            'projcet name': prjct_name,
            'project description': prjct_description,
            'project connections': []}
    
    data = []
    _ = [res for res in result]
    for raw_data in _:
        r_data_piece = raw_data[2].__dict__
        if '_sa_instance_state' in r_data_piece:
            '''removes technical information'''
            r_data_piece.pop('_sa_instance_state')
        data.append(r_data_piece)
    
    return {
            'project status': 'found',
            'projcet name': prjct_name,
            'project description': prjct_description,
            'project connections': data}

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
    """
    connection query to storage_db 

    uses subquery with variant parametrs
    """
    subquery = select(UseProject.id, 
                      literal(name),
                      literal(requirements),
                      literal(host),
                      literal(int(port) if port.isdigit() else None),
                      literal(db_name),
                      literal(db_schema),
                      literal(user),
                      literal(pwd),
                      literal(api_key)).where(UseProject.prjct_name==prjct_name)
    
    sql = insert(UseConnect).from_select( ['prjct_id', 
                                           'cn_name',
                                           'cn_requirements',
                                           'cn_host',
                                           'cn_port',
                                           'cn_db',
                                           'cn_schema',
                                           'cn_user',
                                           'cn_pwd',
                                           'cn_apikey'], select=subquery )
    await session.execute(sql)
    await session.commit()
    
    return{'response': '0k'}
    
    
    
    ## usefull explorations 
    # how to get many results from query 
    """ 
    result = (await session.execute(sql)).all()
    _ = [res[0].__dict__ for res in result]
    for data in _:
        print(data, end='\n\n')
    """
    
     # query examples:
    """ SELECT connections.id, connections.prjct_id, connections.cn_requirements,
    connections.cn_name, connections.cn_host, connections.cn_port,
    connections.cn_user, connections.cn_pwd, connections.cn_db, connections.cn_schema,
    connections.cn_apikey 
    FROM connections JOIN projects ON connections.prjct_id = projects.id """
    # same as 
    """ SELECT * FROM connections JOIN projects ON connections.prjct_id = projects.id """
    """ subquery = select(UseConnect).join(UseProject, UseConnect.prjct_id == UseProject.id)\
               .where(UseProject.prjct_name == prjct_name) """
    
    """ subquery = select(UseProject.id, UseConnect.cn_requirements, UseConnect.cn_name,\
                      UseConnect.cn_host, UseConnect.cn_port, UseConnect.cn_user,\
                      UseConnect.cn_pwd, UseConnect.cn_db, UseConnect.cn_schema, UseConnect.cn_apikey)\
                    .where(UseProject.prjct_name==prjct_name) """

    """ select * from connections left join projects on connections.prjct_id = projects.id where prjct_name='name1';"""

    """ sql = insert(UseConnect).\
        values( prjct_name=prjct_name, prjct_description=prjct_desc, created_at=datetime.now()) """
    
    """ insert into connections (prjct_id, cn_name, cn_host)
values ((select id from projects where  projects.prjct_name = 'name2'), 'YACHOOO', 'yandex.ru');
 """    
   