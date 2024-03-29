from fastapi import APIRouter, Request, Form
from typing import Annotated

from connections.connection_api import APIConnection
from api_routes.form_body_parser import body_parser


router = APIRouter(
    prefix='/session/api-connection',
    tags=['Connection', 'API']
)


@router.post('/update-base-data/')
async def get_start_page(request:Request,  prjct_name:Annotated[str, Form()], cn_name:Annotated[str, Form()],
                   protocol:Annotated[str, Form()], host:Annotated[str, Form()], 
                   port:Annotated[str, Form()], shortcut:Annotated[str, Form()]):
    api = APIConnection()
    api.set_prjct_name(prjct_name=prjct_name)
    api.set_cn_name(cn_name=cn_name)
    await api.load_prjct_and_cn_ids()
    await api.load_base_data_from_db()
    
    api.set_protocol(protocol=protocol)
    api.set_host(host=host)
    api.set_port(port=port)
    api.set_shortcut(shortcut=shortcut)

    await api.update_entry_in_db()
    return 

@router.post('/test/')
async def test (request:Request):
    # ДОЛЖЕН ЛОВИТЬ ЕЩЁ И МЕТОД!
    body = str(await request.body())
    
    mock_method = 'POST'

    body_json = body_parser(body)
    api = APIConnection()
    api.set_prjct_name(prjct_name=body_json["prjct_name"])
    api.set_cn_name(cn_name=body_json["cn_name"])
    await api.load_prjct_and_cn_ids()
    await api.load_base_data_from_db()
    
    print(body_json)
    await api.create_request_path(request_path=body_json['api_path'],
                                  method=mock_method,
                                  headers_vars=body_json['heads'],
                                  body_vars=body_json['bodys'])
    
    api2 = APIConnection()
    api2.set_prjct_name(prjct_name=body_json["prjct_name"])
    api2.set_cn_name(cn_name=body_json["cn_name"])
    await api2.load_prjct_and_cn_ids()
    await api2.load_base_data_from_db()

    await api2.load_advanced_data_from_db()
    return