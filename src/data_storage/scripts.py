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