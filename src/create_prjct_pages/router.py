from fastapi import APIRouter, Request, Form

from typing import Annotated

from fastapi.templating import Jinja2Templates
import requests

router = APIRouter(
    prefix='/pages/prjct',
    tags=['pages', 'project']
)

templates = Jinja2Templates(directory='pages/templates')

@router.get('/')
def get_start_page(request:Request):
    return templates.TemplateResponse('prjct/start_page.html', {'request':request})


# https://fastapi.tiangolo.com/ru/tutorial/background-tasks/
# https://stackoverflow.com/questions/63483246/how-to-call-an-api-from-another-api-in-fastapi
@router.post('/new-project')
def to_a_new_project(request:Request, prjct_name:Annotated[str, Form()],\
                      prjct_description:Annotated[str, Form()]='' ):
    call_create_project(request, prjct_name, prjct_description)
    return templates.TemplateResponse('prjct/new_project_form.html', {'request':request,
                                                          'data':
                                                                { 'prjct_name': prjct_name,
                                                                   'prjct_description': prjct_description 
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
    args = args[:2] + [requirements] + args[3:]

    return {'response': '0k'}

## Utils
def call_create_project(request:Request, prjct_name:str, prjct_description:str):
    HOST = request.base_url
    url = f'{HOST}data/create-project?prjct_name={prjct_name}&prjct_desc={prjct_description}'
    response = requests.post(url)
    return response

def call_create_connect(request:Request, 
                        prjct_name, name, requirements,
                        host, port, db_name, db_schema, user, pwd, api_key):
    HOST = request.base_url
    url = f'{HOST}/data/create-connection?\
            prjct_name={prjct_name}&name={name}&requirements={requirements}&\
            host={host}&port={port}&db_name={db_name}&db_schema={db_schema}&\
            user={user}&pwd={pwd}&api_key={api_key}'
    response = requests.post(url)
    return response


