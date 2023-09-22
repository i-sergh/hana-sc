from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from hana.router import get_table_structure

router = APIRouter(
    prefix='/pages',
    tags=['pages']
)

templates = Jinja2Templates(directory='pages/templates')

@router.get('/')
def get_start_page(request: Request):
    """Возвращает стартовую страницу"""
    return templates.TemplateResponse('base.html', 
                                        {'request': request,})

@router.get('/struct/')
@router.post('/struct/')
def show_table_struct_form(request: Request):
    """Возвращает страницку для получения структуры таблицы"""
  
    return templates.TemplateResponse('table.html', 
                                        {'request': request,
                                          'results': None})


     
@router.post('/struct/{table_name}')
def show_table_struct (request: Request, results=Depends(get_table_structure)):
    """Возвращает страницку для получения структуры таблицы"""
    return templates.TemplateResponse('table.html', 
                                        {'request': request,
                                         'results': results})