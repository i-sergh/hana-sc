from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from hana.router import get_table_structure

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

@router.get('/struct/{prjct_name}/{third_thing}/{cn_name}/')
@router.post('/struct/{prjct_name}/{third_thing}/{cn_name}/')
def show_table_struct_form(request: Request, third_thing, result = Depends(test_args)): #
    """Возвращает страницку для получения структуры таблицы"""
    print(result) 
    print(third_thing)
    return templates.TemplateResponse('table.html', 
                                        {'request': request,
                                          'results': None})


     
@router.post('/struct/{prjct_name}/{cn_name}/{table_name}/')
def show_table_struct (request: Request, results=Depends(get_table_structure)):
    """Возвращает страницку для получения структуры таблицы"""
    return templates.TemplateResponse('table.html', 
                                        {'request': request,
                                         'results': results})

