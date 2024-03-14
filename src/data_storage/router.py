from fastapi import APIRouter, Depends, Request

from sqlalchemy import insert, select, delete, update
from sqlalchemy.sql.expression import literal

from data_storage.models import UseProject, UseConnect
from storage_pgdb import get_async_session, async_session_maker

from datetime import datetime
from functools import wraps
from connections.connection_api import APIConnection

router = APIRouter(
    prefix='/data',
    tags=['Project settings']
)

@router.post('/create-project')
async def create_project(prjct_name:str, prjct_desc:str=None, session=Depends(get_async_session)):
    sql = insert(UseProject).\
        values( prjct_name=prjct_name, prjct_description=prjct_desc, created_at=datetime.now(), last_used_at=datetime.now())
    await session.execute(sql)
    await session.commit()
    return {'message':'success'}

@router.patch('/project-touched')
async def project_touched(prjct_name:str, session=Depends(get_async_session)):
    """
    Called when project has been changing or opening
    """
    sql = update(UseProject).where(UseProject.prjct_name==prjct_name).values(last_used_at=datetime.now())
    result = await session.execute(sql)
    await session.commit()
    if result.rowcount:
        print(prjct_name + ': Data updated successful')
        return {'message': 'Data updated successful'}
    else:
        print('no project named ' + prjct_name)
        return {'message': 'no project named ' + prjct_name}

## UTILS
def touch_project(func):
    """
    Called when project has been changing or opening
    """
    @wraps(func)
    async def wrapper(prjct_name:str, *args, **kwargs):
        async with async_session_maker() as session_:
            sql = update(UseProject).where(UseProject.prjct_name==prjct_name).values(last_used_at=datetime.now())
            result = await session_.execute(sql)
            await session_.commit()
            if result.rowcount:
                print(prjct_name + "'s data successfuly updated")
            else:
                print("No project named " + prjct_name + '\n Nothing to update')
        return await func(prjct_name, *args, **kwargs)
    return wrapper

@router.get('/get-project-info')
async def get_project_info_by_name(name:str, session=Depends(get_async_session)):
    sql = select(UseProject.prjct_name, UseProject.prjct_description, UseProject.created_at).\
            where(UseProject.prjct_name==name)
    result = await session.execute(sql)
    result_list = list(result.all()[0])
    return {'result':result_list}

@router.get('/last-five-projects')
async def get_last_five_projects(session=Depends(get_async_session)):
    sql = select(UseProject.prjct_name, UseProject.prjct_description, UseProject.created_at).\
          order_by(UseProject.last_used_at.desc()).limit(5)
    result_sql = (await session.execute(sql)).all()
    result = []
    for line in result_sql:
        res_line = {}
        res_line['prjct_name'] = line[0]
        res_line['prjct_description'] = line[1]
        res_line['created_at'] = line[2]
        result.append(res_line.copy())
        
    return {"result": result}

@router.get('/retrieve-search-results')
async def retrieve_search_results(search_query:str, max_results:int=5, session=Depends(get_async_session)):
    

    sql = select(UseProject.prjct_name, UseProject.prjct_description, UseProject.created_at).\
          where(UseProject.prjct_name.contains(search_query)).\
          order_by(UseProject.last_used_at.desc()).limit(max_results)

    result_sql = (await session.execute(sql)).all()
    result = []
    for line in result_sql:
        res_line = {}
        res_line['prjct_name'] = line[0]
        res_line['prjct_description'] = line[1]
        res_line['created_at'] = line[2]
        result.append(res_line.copy())
        
    return {"result": result}

@router.get('/get-project-and-connections')
@touch_project
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
        if r_data_piece['cn_drv'] == 'API':
            api = APIConnection()
            api.set_prjct_name(prjct_name=prjct_name)
            api.set_cn_name(cn_name=r_data_piece['cn_name'])
            await api.load_prjct_and_cn_ids()
            await api.load_base_data_from_db()
            r_data_piece['cn_host'] = api.HOST
            r_data_piece['cn_port'] = api.PORT
            r_data_piece['cn_user'] = api.USER
            r_data_piece['cn_pwd'] = api.PASS
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
async def delete_project_by_name(prjct_name:str, session=Depends(get_async_session)):
    sql = delete(UseProject).where(UseProject.prjct_name==prjct_name)
    await session.execute(sql)
    await session.commit()
    return {'message':'success'}

@router.patch('/update-project-description')
@touch_project
async def update_project_description(prjct_name:str, desc:str='', session=Depends(get_async_session)):
    sql = update(UseProject).where(UseProject.prjct_name==prjct_name).values(prjct_description=desc)
    await session.execute(sql)
    await session.commit()
    #touch_project(prjct_name)
    return {'message':'success'}

## connection

@router.post('/create-connection')
async def create_connection(prjct_name:str, name:str, requirements:str, 
                      driver:str, is_target:bool,  
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
                      literal(driver),
                      literal(is_target),
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
                                           'cn_drv',
                                           'cn_is_target',
                                           'cn_host',
                                           'cn_port',
                                           'cn_db',
                                           'cn_schema',
                                           'cn_user',
                                           'cn_pwd',
                                           'cn_apikey'], select=subquery )
    await session.execute(sql)
    await session.commit()
    
    return{'message': '0k'}
    
@router.delete('/delete-connection')   
async def delete_connection(prjct_name:str, c0nnection_name:str,
                             session=Depends(get_async_session)):
    #  delete from connections where prjct_id  = (select id from projects where prjct_name='nasd');

    subquery = select(UseProject.id).where(UseProject.prjct_name==prjct_name).scalar_subquery()
    query = delete(UseConnect).where((UseConnect.prjct_id == subquery)\
                                      & (UseConnect.cn_name==c0nnection_name))
    await session.execute(query)
    await session.commit()
    return{'message': '0k'}
    
@router.get("/conninfo-by-pname-cname")
async def get_connection_info_by_prjct_name_cn_name(prjct_name:str, cn_name:str,
                                       session=Depends(get_async_session)):
    print('in query')
    # select * from connections 
    # where connections.prjct_id =  (select projects.id from projects where projects.prjct_name = 'prjct' )
    # and connections.cn_name = 'ConnectHana';
    subquery = select(UseProject.id).where(UseProject.prjct_name==prjct_name).scalar_subquery()
    sql = select(UseConnect)\
          .where((UseConnect.prjct_id ==subquery)
                  & (UseConnect.cn_name == cn_name)) 
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
    result['DRIVER'] = result_sql['cn_drv'] 
    result['USER'] = result_sql['cn_user']
    result['PASS'] = result_sql['cn_pwd']
    result['HOST'] = result_sql['cn_host']
    result['PORT'] = result_sql['cn_port']
    result['NAME'] = result_sql['cn_db']
    result['SCHEMA'] = result_sql['cn_schema']
    result['APIKEY'] = result_sql['cn_apikey']
    
    return result





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
   