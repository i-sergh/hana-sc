import asyncio

from fastapi import APIRouter, Request, Form, Depends

from typing import Annotated

from fastapi.templating import Jinja2Templates
import requests

from storage_pgdb import get_async_session
from data_storage.router import get_last_five_projects
#### !!!!!!
from data_storage.scripts import create_connection_entry
from connections.connection_api import APIConnection


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
async def create_new_connection_form_handler(request:Request, prjct_name:Annotated[str, Form()], cn_name:Annotated[str, Form()],
         driver:Annotated[str, Form()], is_target:Annotated[bool, Form()]=False,
        host:Annotated[str, Form()]="", port:Annotated[str, Form()]="",
        db_name:Annotated[str, Form()]="", db_schema:Annotated[str, Form()]="",
        user:Annotated[str, Form()]="", pwd:Annotated[str, Form()]="",
        api_key:Annotated[str, Form()]=""):
    args = [prjct_name, cn_name, driver, is_target, host, port, db_name, db_schema, user, pwd, api_key]

    #TODO: remove indexation of all required fields (maybe remove completely 'requirements' field)
    requirements = ['1' if arg else '0'  for arg in args]
    requirements = ''.join(requirements[2:])
    args = args[:2] + [requirements] + args[2:]

    keys = ['prjct_name','cn_name','requirements', 'driver', 'is_target',  
                        'host', 'port', 'db_name', 'db_schema', 'user', 'pwd', 'api_key']
    kwargs = dict([[key, arg] for key,arg in zip(keys, args)])
            #########
       ############
    ####################################
       ############
            #########
    # creates general connection entry 
    
    await create_connection_entry(**kwargs)
    if driver == "API":
        api = APIConnection(HOST=host, PORT=port, USER=user, PASS=pwd) 
        api.set_cn_name(cn_name)
        api.set_prjct_name(prjct_name)
        await api.load_prjct_and_cn_ids()
        await api.init_new_entry_in_db()

    
    return {'response': '0k'}

## Utils
def call_create_project(request:Request, prjct_name:str, prjct_description:str):
    HOST = request.base_url
    
    url = f'{HOST}data/create-project?prjct_name={prjct_name}&prjct_desc={prjct_description}'
    response = requests.post(url)
    
    return response

def call_get_project_and_connections(request:Request, prjct_name:str):
    HOST = request.base_url
    url = f'{HOST}data/get-project-and-connections?prjct_name={prjct_name}'
    
    response = requests.get(url)
    
    return response

