from sqlalchemy import insert, select, delete, update
from sqlalchemy.sql.expression import literal

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
    #print(result_sql)
    result = {}
    result['USER'] = result_sql['cn_user']
    result['PASS'] = result_sql['cn_pwd']
    result['DRIVER'] = result_sql['cn_drv']
    result['TRGT'] = result_sql['cn_is_target']
    result['HOST'] = result_sql['cn_host']
    result['PORT'] = result_sql['cn_port']
    result['NAME'] = result_sql['cn_db']
    result['SCHEMA'] = result_sql['cn_schema']
    result['APIKEY'] = result_sql['cn_apikey']
    return result

async def create_connection_entry(prjct_name:str, cn_name:str, requirements:str, 
                      driver:str, is_target:bool,  
                      host:str="", port:str="", db_name:str="",
                      db_schema:str="", user:str="", pwd:str="",
                      api_key:str=""):

    async with async_session_maker() as session:
        subquery = select(UseProject.id, 
                        literal(cn_name),
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
