from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

#from hana.router import get_table_structure

from connections.connection_db import is_connection_session, is_schema_saved
from connections.router import get_table_structure

router = APIRouter(
    prefix='/pages',
    tags=['pages']
)

templates = Jinja2Templates(directory='pages/templates')

@router.post('/test/args/')
def test_args(prjct_name, cn_name):
    return {"prjct_name": prjct_name, "cn_name": cn_name}

@router.get('/')
def get_start_page(request: Request):
    """Возвращает стартовую страницу"""
    return templates.TemplateResponse('base.html', 
                                        {'request': request,})

#@router.get('/struct/{prjct_name}/{cn_name}/')
@router.post('/struct/{prjct_name}/{cn_name}/')
def show_table_struct_form(request: Request, prjct_name:str, cn_name:str): #
    """Возвращает страницку для получения структуры таблицы"""
    is_session = is_connection_session(cn_name=cn_name, prjct_name=prjct_name)
    has_schema = is_schema_saved(prjct_name=prjct_name, cn_name=cn_name)
    
    return templates.TemplateResponse('table.html', 
                                        {'request': request,
                                         'is_session': is_session,
                                         'has_schema': has_schema,
                                         'prjct_name': prjct_name,
                                         'cn_name': cn_name,
                                          'results': None})


     
@router.post('/struct/{prjct_name}/{cn_name}/{table_name}/')
def show_table_struct (request: Request,cn_name:str, prjct_name:str,table_name:str, results=Depends(get_table_structure)):
    """Возвращает страницку для получения структуры таблицы"""
    return templates.TemplateResponse('table.html', 
                                        {'request': request,
                                         'prjct_name': prjct_name,
                                         'cn_name':cn_name,
                                         'table_name':table_name,
                                         'results': results})

