from fastapi import APIRouter, Request, Form, Depends

from typing import Annotated

from fastapi.templating import Jinja2Templates
import requests

from storage_pgdb import get_async_session
from data_storage.router import get_last_five_projects

router = APIRouter(
    prefix='/pages/prjct',
    tags=['pages', 'project']
)

templates = Jinja2Templates(directory='pages/templates')

@router.get('/')
def get_start_page(request:Request, last_five_prjcts=Depends(get_last_five_projects)):
    return templates.TemplateResponse('prjct/start_page.html', {"request":request,
                                                                "data":last_five_prjcts})


# https://fastapi.tiangolo.com/ru/tutorial/background-tasks/
# https://stackoverflow.com/questions/63483246/how-to-call-an-api-from-another-api-in-fastapi
@router.post('/new-project')
def to_a_new_project(request:Request, prjct_name:Annotated[str, Form()],\
                      prjct_description:Annotated[str, Form()]=''):
    response = call_get_project_and_connections(request, prjct_name).json()
    
    if response['project status'] == 'no project':
        call_create_project(request, prjct_name, prjct_description)
        return templates.TemplateResponse('prjct/new_project_form.html', {'request':request,
                                                                            'data':
                                                                            { 'prjct_name': prjct_name,
                                                                              'prjct_description': prjct_description,
                                                                              'connections': []
                                                                         }})
    return templates.TemplateResponse('prjct/new_project_form.html', {'request':request,
                                                                        'data':
                                                                            { 'prjct_name': response['projcet name'],
                                                                              'prjct_description': response['project description'],
                                                                              'connections':  response['project connections']
                                                                            }})


## TODO: DECORATOR NO SPACE IN STRING ENSHUER 
@router.post('/open-project')
def to_a_new_project(request:Request, prjct_name:str):
    response = call_get_project_and_connections(request, prjct_name).json()
    if response['project status'] == 'no project':
        return {"message": "no project"}
    return templates.TemplateResponse('prjct/new_project_form.html', {'request':request,
                                                                        'data':
                                                                            { 'prjct_name': response['projcet name'],
                                                                              'prjct_description': response['project description'],
                                                                              'connections':  response['project connections']
                                                                            }})


@router.post('/new-connection')
def test(request:Request, prjct_name:Annotated[str, Form()], name:Annotated[str, Form()], 
        host:Annotated[str, Form()]="", port:Annotated[str, Form()]="",
        db_name:Annotated[str, Form()]="", db_schema:Annotated[str, Form()]="",
        user:Annotated[str, Form()]="", pwd:Annotated[str, Form()]="",
        api_key:Annotated[str, Form()]=""):

    args = [prjct_name, name, host, port, db_name, db_schema, user, pwd, api_key]

    requirements = ['1' if arg else '0'  for arg in args]
    requirements = ''.join(requirements[2:])
    args = args[:2] + [requirements] + args[2:]

    keys = ['prjct_name', 'name', 'requirements',
                        'host', 'port', 'db_name', 'db_schema', 'user', 'pwd', 'api_key']
    kwargs = dict([[key, arg] for key,arg in zip(keys, args)])
    call_create_connect(request, **kwargs)
    return {'response': '0k'}

## Utils
def call_create_project(request:Request, prjct_name:str, prjct_description:str):
    HOST = request.base_url
    print(HOST)
    url = f'{HOST}data/create-project?prjct_name={prjct_name}&prjct_desc={prjct_description}'
    response = requests.post(url)
    
    return response

def call_create_connect(request:Request, **kwargs):
    HOST = request.base_url
    print(HOST)
    url = f'{HOST}data/create-connection?prjct_name={kwargs["prjct_name"]}&name={kwargs["name"]}&requirements={kwargs["requirements"]}&host={kwargs["host"]}&port={kwargs["port"]}&db_name={kwargs["db_name"]}&db_schema={kwargs["db_schema"]}&user={kwargs["user"]}&pwd={kwargs["pwd"]}&api_key={kwargs["api_key"]}' 
    response = requests.post(url)
    return response

def call_get_project_and_connections(request:Request, prjct_name:str):
    HOST = request.base_url
    url = f'{HOST}data/get-project-and-connections?prjct_name={prjct_name}'
    print(url)
    response = requests.get(url)
    return response

